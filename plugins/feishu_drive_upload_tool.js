/**
 * Copyright (c) 2026
 * SPDX-License-Identifier: MIT
 *
 * Feishu Drive Upload Tool - OpenClaw Tool Registration
 * 飞书云盘文件上传工具 - OpenClaw工具注册
 *
 * 功能:
 * - 上传本地文件到飞书云空间
 * - 自动处理大文件(>20MB压缩/分割)
 * - 支持文件夹token指定上传位置
 * - 自动获取tenant_access_token
 */

const { registerTool, createToolContext, assertLarkOk, json } = require('./helpers');
const { Type } = require('@sinclair/typebox');
const fs = require('fs/promises');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB
const FEISHU_CONFIG = {
  appId: process.env.FEISHU_APP_ID || 'cli_a949c1e2f4f89cb3',
  appSecret: process.env.FEISHU_APP_SECRET || 'Z8hnq3wLrkjQrCes94N0xEqBlHPHjk6b'
};

// Schema定义
const FeishuDriveUploadSchema = Type.Object({
  action: Type.Union([
    Type.Literal('upload'),
    Type.Literal('upload_large'),
    Type.Literal('list')
  ], {
    description: '操作类型：upload(普通上传), upload_large(大文件处理上传), list(列出文件)'
  }),
  file_path: Type.Optional(Type.String({
    description: '本地文件路径（upload/upload_large时需要）'
  })),
  parent_node: Type.Optional(Type.String({
    description: '目标文件夹token（可选，默认为根目录）'
  })),
  compress: Type.Optional(Type.Boolean({
    description: '是否压缩为ZIP（默认自动判断）'
  })),
  file_name: Type.Optional(Type.String({
    description: '自定义文件名（可选，默认使用原文件名）'
  }))
});

/**
 * 获取tenant_access_token
 */
async function getTenantToken(client) {
  const result = await client.invoke('feishu_auth', (sdk, opts) => 
    sdk.auth.tenantAccessToken.internal({
      data: {
        app_id: FEISHU_CONFIG.appId,
        app_secret: FEISHU_CONFIG.appSecret
      }
    }, opts)
  );
  
  if (result.code !== 0) {
    throw new Error(`获取token失败: ${result.msg}`);
  }
  
  return result.tenant_access_token;
}

/**
 * 压缩文件为ZIP
 */
async function compressToZip(filePath, outputDir) {
  const fileName = path.basename(filePath);
  const zipPath = path.join(outputDir, `${fileName}.zip`);
  
  // 使用系统zip命令
  execSync(`zip -j "${zipPath}" "${filePath}"`, { stdio: 'pipe' });
  
  return zipPath;
}

/**
 * 分割大文件为多个ZIP
 */
async function splitLargeFile(filePath, outputDir, maxSize = MAX_FILE_SIZE) {
  const fileSize = (await fs.stat(filePath)).size;
  
  if (fileSize <= maxSize) {
    return [filePath];
  }
  
  // 先压缩
  const zipPath = await compressToZip(filePath, outputDir);
  const zipSize = (await fs.stat(zipPath)).size;
  
  if (zipSize <= maxSize) {
    return [zipPath];
  }
  
  // 压缩后仍超限，分割ZIP
  const numParts = Math.ceil(zipSize / maxSize);
  const parts = [];
  const baseName = path.basename(filePath, path.extname(filePath));
  
  for (let i = 0; i < numParts; i++) {
    const partPath = path.join(outputDir, `${baseName}_part${i + 1}.zip`);
    parts.push(partPath);
  }
  
  return parts;
}

/**
 * 读取文件为Buffer
 */
async function readFileBuffer(filePath) {
  return await fs.readFile(filePath);
}

/**
 * 注册工具
 */
function registerFeishuDriveUploadTool(api) {
  if (!api.config) return false;
  
  const { toolClient, log } = createToolContext(api, 'feishu_drive_upload');
  
  return registerTool(api, {
    name: 'feishu_drive_upload',
    label: 'Feishu Drive Upload',
    description: '【飞书云盘上传】上传本地文件到飞书云空间。支持自动压缩和分割大文件(>20MB)。\n\nActions:\n- upload: 上传文件（自动处理大小）\n- upload_large: 强制处理大文件（压缩+分割）\n- list: 列出云空间文件\n\n参数:\n- file_path: 本地文件路径\n- parent_node: 目标文件夹token（可选，默认根目录）\n- compress: 是否强制压缩（可选）\n- file_name: 自定义文件名（可选）\n\n返回:\n- file_token: 文件在云空间的token\n- file_name: 实际文件名\n- size: 文件大小\n- method: 上传方式（direct/compressed/split）',
    parameters: FeishuDriveUploadSchema,
    
    async execute(_toolCallId, params) {
      const p = params;
      
      try {
        const client = toolClient();
        
        // -----------------------------------------------------------------
        // LIST - 列出文件
        // -----------------------------------------------------------------
        if (p.action === 'list') {
          log.info('list: 获取云空间文件列表');
          
          const res = await client.invoke('feishu_drive_upload', (sdk, opts) => 
            sdk.drive.file.list({
              params: {
                page_size: 200
              }
            }, opts)
          );
          
          assertLarkOk(res);
          
          return json({
            files: res.data?.files || [],
            has_more: res.data?.has_more || false,
            count: res.data?.files?.length || 0
          });
        }
        
        // -----------------------------------------------------------------
        // UPLOAD / UPLOAD_LARGE - 上传文件
        // -----------------------------------------------------------------
        if (!p.file_path) {
          return json({ error: 'file_path is required for upload/upload_large action' });
        }
        
        // 检查文件
        try {
          await fs.access(p.file_path);
        } catch {
          return json({ error: `File not found: ${p.file_path}` });
        }
        
        const filePath = p.file_path;
        const fileName = p.file_name || path.basename(filePath);
        const fileStat = await fs.stat(filePath);
        const fileSize = fileStat.size;
        
        log.info(`upload: file=${fileName}, size=${fileSize}, parent=${p.parent_node || '(root)'}`);
        
        // 判断处理方式
        let filesToUpload = [];
        let uploadMethod = 'direct';
        let tempDir = null;
        
        if (p.action === 'upload_large' || fileSize > MAX_FILE_SIZE || p.compress) {
          // 需要处理大文件
          const os = require('os');
          tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'feishu-upload-'));
          
          if (fileSize > MAX_FILE_SIZE || p.action === 'upload_large') {
            log.info(`upload: 文件过大，进行压缩/分割处理`);
            uploadMethod = fileSize > MAX_FILE_SIZE * 2 ? 'split' : 'compressed';
            
            try {
              const parts = await splitLargeFile(filePath, tempDir, MAX_FILE_SIZE);
              filesToUpload = parts;
            } catch (err) {
              log.error(`upload: 文件处理失败: ${err.message}`);
              return json({ error: `File processing failed: ${err.message}` });
            }
          } else {
            // 仅压缩
            uploadMethod = 'compressed';
            const zipPath = await compressToZip(filePath, tempDir);
            filesToUpload = [zipPath];
          }
        } else {
          // 直接上传
          filesToUpload = [filePath];
        }
        
        log.info(`upload: 将上传 ${filesToUpload.length} 个文件`);
        
        // 逐个上传
        const results = [];
        
        for (let i = 0; i < filesToUpload.length; i++) {
          const uploadFile = filesToUpload[i];
          const uploadFileName = filesToUpload.length > 1 
            ? `${fileName}_part${i + 1}` 
            : fileName;
          const uploadSize = (await fs.stat(uploadFile)).size;
          
          log.info(`upload: 上传文件 ${i + 1}/${filesToUpload.length}: ${uploadFileName}`);
          
          // 读取文件内容
          const fileBuffer = await readFileBuffer(uploadFile);
          
          // 执行上传
          const res = await client.invoke('feishu_drive_upload', (sdk, opts) =>
            sdk.drive.file.uploadAll({
              data: {
                file_name: uploadFileName,
                parent_type: 'explorer',
                parent_node: p.parent_node || '',
                size: uploadSize,
                file: fileBuffer
              }
            }, opts)
          );
          
          assertLarkOk(res);
          
          results.push({
            file_token: res.data?.file_token,
            file_name: uploadFileName,
            size: uploadSize,
            part: filesToUpload.length > 1 ? i + 1 : null
          });
          
          log.info(`upload: 文件 ${i + 1} 上传成功, token=${res.data?.file_token}`);
        }
        
        // 清理临时文件
        if (tempDir) {
          try {
            await fs.rm(tempDir, { recursive: true });
          } catch (e) {
            log.warn(`upload: 清理临时文件失败: ${e.message}`);
          }
        }
        
        return json({
          success: true,
          method: uploadMethod,
          total_parts: results.length,
          files: results,
          original_file: {
            path: filePath,
            name: fileName,
            size: fileSize
          }
        });
        
      } catch (err) {
        log.error(`upload: 执行失败: ${err.message}`);
        return json({
          error: err.message,
          stack: err.stack
        });
      }
    }
  });
}

module.exports = { registerFeishuDriveUploadTool };

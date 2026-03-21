# nacos_ai_registry.py - Nacos 3.2 AI Registry Implementation
# Simplified autonomous implementation

import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class Skill:
    """MCP Skill Registry Entry"""
    id: str
    name: str
    version: str
    description: str
    endpoint: str
    parameters: Dict
    created_at: str
    updated_at: str
    
@dataclass
class Prompt:
    """Prompt Registry Entry"""
    id: str
    name: str
    version: str
    template: str
    variables: List[str]
    created_at: str
    updated_at: str

@dataclass
class Agent:
    """Agent Registry Entry"""
    id: str
    name: str
    capabilities: List[str]
    endpoint: str
    status: str  # online, offline, busy
    last_heartbeat: str

@dataclass
class MCPConnection:
    """MCP Registry Entry"""
    id: str
    server_name: str
    transport: str  # stdio, sse
    config: Dict
    status: str

class NacosAIRegistry:
    """
    Nacos 3.2 AI Registry - Four Registry Implementation
    - Skill Registry
    - Prompt Registry  
    - Agent Registry
    - MCP Registry
    """
    
    def __init__(self, namespace: str = "satisficing"):
        self.namespace = namespace
        self.skills: Dict[str, Skill] = {}
        self.prompts: Dict[str, Prompt] = {}
        self.agents: Dict[str, Agent] = {}
        self.mcp_connections: Dict[str, MCPConnection] = {}
        
        # Initialize with Satisficing Institute defaults
        self._init_default_skills()
        self._init_default_prompts()
        self._init_default_agents()
    
    def _init_default_skills(self):
        """Initialize Satisficing Institute skills"""
        default_skills = [
            {
                "name": "partner_evaluation",
                "description": "合伙人评估与匹配",
                "parameters": {"partner_context": "object"}
            },
            {
                "name": "risk_analysis",
                "description": "风险评估与分析",
                "parameters": {"risk_factors": "array"}
            },
            {
                "name": "decision_gene_test",
                "description": "决策基因体检",
                "parameters": {"decision_history": "array"}
            },
            {
                "name": "pfi_scorecard",
                "description": "PFI评分卡生成",
                "parameters": {"partner_data": "object"}
            },
            {
                "name": "conflict_resolution",
                "description": "冲突调解分析",
                "parameters": {"conflict_context": "object"}
            }
        ]
        
        for skill_def in default_skills:
            self.register_skill(
                name=skill_def["name"],
                version="1.0.0",
                description=skill_def["description"],
                parameters=skill_def["parameters"]
            )
    
    def _init_default_prompts(self):
        """Initialize expert digital twin prompts"""
        default_prompts = [
            {
                "name": "li_honglei_philosophy",
                "template": """你现在是黎红雷教授的数字替身，儒商哲学专家。
                
问题: {question}

请以儒商哲学的视角分析，强调：
1. 合伙人关系中的伦理维度
2. 长期主义的价值观
3. 和谐共生的商业哲学

回答:""",
                "variables": ["question"]
            },
            {
                "name": "luohan_math",
                "template": """你现在是罗汉教授的数字替身，数学建模专家。

问题: {question}

请以数学严谨性分析：
1. 建立量化模型
2. 给出可计算的指标
3. 提供置信区间

回答:""",
                "variables": ["question"]
            },
            {
                "name": "xie_baojian_strategy",
                "template": """你现在是谢宝剑研究员的数字替身，深港战略专家。

问题: {question}

请从战略视角分析：
1. 区域发展机遇
2. 政策环境评估
3. 地理优势分析

回答:""",
                "variables": ["question"]
            }
        ]
        
        for prompt_def in default_prompts:
            self.register_prompt(
                name=prompt_def["name"],
                version="1.0.0",
                template=prompt_def["template"],
                variables=prompt_def["variables"]
            )
    
    def _init_default_agents(self):
        """Initialize 33 Satisficing Institute agents"""
        # Executive layer (5)
        executives = [
            ("orchestrator", "任务编排Agent", ["task_decomposition", "agent_coordination"]),
            ("evaluator", "质量评估Agent", ["quality_assurance", "consensus_voting"]),
            ("integrator", "结果整合Agent", ["report_generation", "multi_source_fusion"]),
            ("communicator", "客户沟通Agent", ["client_interaction", "progress_reporting"]),
            ("monitor", "实时监控Agent", ["performance_tracking", "anomaly_detection"])
        ]
        
        # Expert layer (6)
        experts = [
            ("li_honglei_expert", "黎红雷教授替身", ["confucian_ethics", "partnership_morality"]),
            ("luohan_expert", "罗汉教授替身", ["mathematical_modeling", "algorithm_design"]),
            ("xie_baojian_expert", "谢宝剑研究员替身", ["regional_strategy", "policy_analysis"]),
            ("xu_expert", "XU先生替身", ["stress_testing", "ai_systems"]),
            ("fang_yifeng_expert", "方翊沣博士替身", ["perception_training", "bci"]),
            ("chen_guoxiang_expert", "陈国祥博士替身", ["energy_therapy", "wellness"])
        ]
        
        # Execution layer (22)
        for i in range(22):
            executives.append((f"executor_{i+1}", f"执行Agent-{i+1}", ["task_execution", "data_processing"]))
        
        for agent_id, name, caps in executives + experts:
            self.register_agent(
                id=agent_id,
                name=name,
                capabilities=caps,
                endpoint=f"https://satisficing.ai/agents/{agent_id}"
            )
    
    # ============ Skill Registry ============
    
    def register_skill(self, name: str, version: str, description: str, 
                      parameters: Dict, endpoint: str = "") -> str:
        """Register a new skill"""
        skill_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        skill = Skill(
            id=skill_id,
            name=name,
            version=version,
            description=description,
            endpoint=endpoint or f"/skills/{name}",
            parameters=parameters,
            created_at=now,
            updated_at=now
        )
        
        self.skills[name] = skill
        print(f"✅ Registered skill: {name} v{version}")
        return skill_id
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict]:
        """List all registered skills"""
        return [asdict(skill) for skill in self.skills.values()]
    
    def discover_skills(self, capability: str) -> List[Skill]:
        """Discover skills by capability"""
        return [
            skill for skill in self.skills.values()
            if capability.lower() in skill.description.lower()
        ]
    
    # ============ Prompt Registry ============
    
    def register_prompt(self, name: str, version: str, template: str,
                       variables: List[str]) -> str:
        """Register a new prompt template"""
        prompt_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        prompt = Prompt(
            id=prompt_id,
            name=name,
            version=version,
            template=template,
            variables=variables,
            created_at=now,
            updated_at=now
        )
        
        self.prompts[name] = prompt
        print(f"✅ Registered prompt: {name} v{version}")
        return prompt_id
    
    def get_prompt(self, name: str, **kwargs) -> str:
        """Get prompt with variables filled"""
        prompt = self.prompts.get(name)
        if not prompt:
            return f"[Prompt {name} not found]"
        
        template = prompt.template
        for var in prompt.variables:
            value = kwargs.get(var, f"{{{var}}}")
            template = template.replace(f"{{{var}}}", str(value))
        
        return template
    
    def list_prompts(self) -> List[Dict]:
        """List all registered prompts"""
        return [asdict(prompt) for prompt in self.prompts.values()]
    
    # ============ Agent Registry ============
    
    def register_agent(self, id: str, name: str, capabilities: List[str],
                      endpoint: str) -> str:
        """Register a new agent"""
        now = datetime.now().isoformat()
        
        agent = Agent(
            id=id,
            name=name,
            capabilities=capabilities,
            endpoint=endpoint,
            status="online",
            last_heartbeat=now
        )
        
        self.agents[id] = agent
        print(f"✅ Registered agent: {name} ({id})")
        return id
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self, status: Optional[str] = None) -> List[Dict]:
        """List all registered agents"""
        agents = self.agents.values()
        if status:
            agents = [a for a in agents if a.status == status]
        return [asdict(agent) for agent in agents]
    
    def discover_agents(self, capability: str) -> List[Agent]:
        """Discover agents by capability"""
        return [
            agent for agent in self.agents.values()
            if any(capability.lower() in cap.lower() for cap in agent.capabilities)
        ]
    
    def heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.last_heartbeat = datetime.now().isoformat()
            agent.status = "online"
            return True
        return False
    
    # ============ MCP Registry ============
    
    def register_mcp(self, server_name: str, transport: str, config: Dict) -> str:
        """Register MCP server connection"""
        mcp_id = str(uuid.uuid4())
        
        mcp = MCPConnection(
            id=mcp_id,
            server_name=server_name,
            transport=transport,
            config=config,
            status="connected"
        )
        
        self.mcp_connections[server_name] = mcp
        print(f"✅ Registered MCP: {server_name} ({transport})")
        return mcp_id
    
    def get_mcp(self, server_name: str) -> Optional[MCPConnection]:
        """Get MCP connection by name"""
        return self.mcp_connections.get(server_name)
    
    def list_mcp(self) -> List[Dict]:
        """List all MCP connections"""
        return [asdict(mcp) for mcp in self.mcp_connections.values()]
    
    # ============ Statistics ============
    
    def get_stats(self) -> Dict:
        """Get registry statistics"""
        return {
            "namespace": self.namespace,
            "skills": len(self.skills),
            "prompts": len(self.prompts),
            "agents": len(self.agents),
            "mcp_connections": len(self.mcp_connections),
            "total": len(self.skills) + len(self.prompts) + len(self.agents) + len(self.mcp_connections)
        }
    
    def export_config(self) -> Dict:
        """Export full registry configuration"""
        return {
            "namespace": self.namespace,
            "skills": self.list_skills(),
            "prompts": self.list_prompts(),
            "agents": self.list_agents(),
            "mcp": self.list_mcp()
        }
    
    def save_to_file(self, filepath: str):
        """Save registry to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_config(), f, indent=2, ensure_ascii=False)
        print(f"💾 Registry saved to: {filepath}")

def demo():
    """Demo: Nacos 3.2 AI Registry"""
    
    print("=" * 60)
    print("Nacos 3.2 AI Registry Demo")
    print("Satisficing Institute - Four Registry Implementation")
    print("=" * 60)
    
    # Initialize registry
    registry = NacosAIRegistry(namespace="satisficing")
    
    print("\n📊 Registry Statistics:")
    stats = registry.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Demo: Skill Discovery
    print("\n🔍 Skill Discovery (capability: '评估'):")
    skills = registry.discover_skills("评估")
    for skill in skills:
        print(f"  • {skill.name}: {skill.description}")
    
    # Demo: Prompt Usage
    print("\n📝 Prompt Template Usage:")
    prompt_text = registry.get_prompt(
        "li_honglei_philosophy",
        question="合伙人信任危机如何处理？"
    )
    print(f"  Generated prompt:\n{prompt_text[:200]}...")
    
    # Demo: Agent Discovery
    print("\n🤖 Agent Discovery (capability: 'ethics'):")
    agents = registry.discover_agents("ethics")
    for agent in agents:
        print(f"  • {agent.name}: {agent.capabilities}")
    
    # Demo: MCP Registration
    print("\n🔌 MCP Registration:")
    registry.register_mcp(
        server_name="github_tools",
        transport="stdio",
        config={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}
    )
    registry.register_mcp(
        server_name="filesystem",
        transport="stdio",
        config={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"]}
    )
    
    print("\n📋 MCP Connections:")
    for mcp in registry.list_mcp():
        print(f"  • {mcp['server_name']} ({mcp['transport']}): {mcp['status']}")
    
    # Save configuration
    print("\n💾 Saving Registry Configuration...")
    registry.save_to_file("/root/.openclaw/workspace/nacos_registry_config.json")
    
    print("\n" + "=" * 60)
    print("Demo Complete - Nacos 3.2 AI Registry Ready")
    print("=" * 60)

if __name__ == "__main__":
    demo()

from app.agents.nus_agent import NUSAgent
from app.agents.ntu_agent import NTUAgent
from app.agents.sit_agent import SITAgent
from app.agents.smu_agent import SMUAgent
from app.agents.suss_agent import SUSSAgent
from app.agents.sutd_agent import SUTDAgent

REGISTRY: dict[str, type] = {
    "NUS": NUSAgent,
    "NTU": NTUAgent,
    "SMU": SMUAgent,
    "SUSS": SUSSAgent,
    "SUTD": SUTDAgent,
    "SIT": SITAgent,
}

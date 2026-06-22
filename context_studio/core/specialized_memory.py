from typing import List, Dict, Any, Optional
from context_studio.providers.base import RelationalProvider
import uuid

class SpecializedMemory:
    """
    Tier 4, 5, 6: Specialized Memory
    Handles Procedural Rules, User Preferences, and Org/Tenant-wide variables.
    """
    def __init__(self, relational_provider: RelationalProvider):
        self.provider = relational_provider

    # Tier 4: Procedural Memory (Rules)
    async def add_rule(self, tenant_id: str, agent_id: Optional[str], name: str, rule_type: str, trigger: str, action: str):
        rule_data = {
            "type": "procedural_rule",
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "agent_id": agent_id,
            "name": name,
            "rule_type": rule_type,
            "trigger_condition": trigger,
            "action_sequence": action,
            "priority": 50
        }
        # In a real system, these go to a dedicated 'procedural_rules' table
        await self.provider.save_turn("system_rules", rule_data)
        
    async def get_active_rules(self, tenant_id: str, agent_id: Optional[str]) -> List[Dict[str, Any]]:
        # Mock retrieval
        return await self.provider.search_relational("procedural_rule")

    # Tier 5: User Preference Memory
    async def update_user_preference(self, tenant_id: str, user_id: str, prefs: Dict[str, Any]):
        pref_data = {
            "type": "user_preference",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "preferences": prefs
        }
        await self.provider.save_turn("system_prefs", pref_data)
        
    async def get_user_preferences(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        # Mock retrieval
        results = await self.provider.search_relational("user_preference")
        for r in results:
            if r.get("user_id") == user_id:
                return r.get("preferences", {})
        return {}

    # Tier 6: Organizational Memory
    async def set_org_variable(self, tenant_id: str, key: str, value: Any):
        org_data = {
            "type": "org_memory",
            "tenant_id": tenant_id,
            "key": key,
            "value": value
        }
        await self.provider.save_turn("system_org", org_data)

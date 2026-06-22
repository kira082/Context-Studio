import os
import casbin
from typing import Optional

class RBACManager:
    """
    Manages Role-Based Access Control (RBAC) using PyCasbin.
    Enforces tenant-isolated access to sessions and objects.
    """
    def __init__(self, model_path: Optional[str] = None, policy_path: Optional[str] = None):
        if not model_path:
            # Default to the conf file in the same directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "casbin_model.conf")
            
        if not policy_path:
            # Default offline policy file
            data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.data/auth"))
            os.makedirs(data_dir, exist_ok=True)
            policy_path = os.path.join(data_dir, "policy.csv")
            if not os.path.exists(policy_path):
                open(policy_path, 'w').close()
                
        self.enforcer = casbin.Enforcer(model_path, policy_path)
        
    def enforce(self, sub: str, tenant: str, obj: str, act: str) -> bool:
        """
        Check if a subject has permission to perform an action on an object within a tenant.
        """
        return self.enforcer.enforce(sub, tenant, obj, act)
        
    def add_policy(self, sub: str, tenant: str, obj: str, act: str) -> bool:
        """
        Add an explicit grant policy.
        """
        added = self.enforcer.add_policy(sub, tenant, obj, act)
        if added:
            self.enforcer.save_policy()
        return added
        
    def add_role_for_user(self, user: str, role: str) -> bool:
        """
        Assign a role to a user.
        """
        added = self.enforcer.add_grouping_policy(user, role)
        if added:
            self.enforcer.save_policy()
        return added
        
    def remove_policy(self, sub: str, tenant: str, obj: str, act: str) -> bool:
        """
        Remove a specific policy.
        """
        removed = self.enforcer.remove_policy(sub, tenant, obj, act)
        if removed:
            self.enforcer.save_policy()
        return removed

    def auto_grant_session_access(self, agent_id: str, tenant_id: str, session_id: str):
        """
        Convenience method to grant an agent read_write access to a session it created.
        """
        self.add_policy(agent_id, tenant_id, session_id, "read")
        self.add_policy(agent_id, tenant_id, session_id, "write")

import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Database } from 'lucide-react';

export default function MemoryNode({ data }: { data: any }) {
  return (
    <div className="custom-node">
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon icon-memory">
          <Database size={14} />
        </div>
        <span>{data.label || 'Context Studio'}</span>
      </div>
      
      <div className="node-content">
        <div>Action: {data.action || 'Retrieve Context'}</div>
        <div style={{ marginTop: 4, color: '#6366f1' }}>{data.tier || 'All Memory Tiers'}</div>
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

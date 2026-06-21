import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Zap } from 'lucide-react';

export default function TriggerNode({ data }: { data: any }) {
  return (
    <div className="custom-node" style={{ borderColor: 'rgba(245, 158, 11, 0.4)' }}>
      <div className="node-header">
        <div className="node-icon icon-trigger">
          <Zap size={14} />
        </div>
        <span>{data.label || 'Trigger'}</span>
      </div>
      
      <div className="node-content">
        <div>{data.description || 'Starts the workflow'}</div>
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

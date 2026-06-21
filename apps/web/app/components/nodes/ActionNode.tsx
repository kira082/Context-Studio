import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Play } from 'lucide-react';

export default function ActionNode({ data }: { data: any }) {
  return (
    <div className="custom-node">
      <Handle type="target" position={Position.Left} />
      
      <div className="node-header">
        <div className="node-icon icon-action">
          <Play size={14} />
        </div>
        <span>{data.label || 'Action'}</span>
      </div>
      
      <div className="node-content">
        <div>{data.description || 'Executes a task'}</div>
      </div>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

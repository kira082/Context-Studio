import React from 'react';
import { Database, Play, Zap } from 'lucide-react';

export default function Sidebar() {
  const onDragStart = (event: React.DragEvent, nodeType: string, label: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.setData('application/label', label);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="sidebar glass-panel">
      <h3 style={{ marginTop: 0, marginBottom: '20px', fontSize: '16px', fontWeight: '600' }}>
        Nodes
      </h3>
      
      <div 
        className="draggable-item" 
        onDragStart={(event) => onDragStart(event, 'triggerNode', 'Webhook Trigger')} 
        draggable
      >
        <div className="node-icon icon-trigger"><Zap size={14} /></div>
        Webhook Trigger
      </div>
      
      <div 
        className="draggable-item" 
        onDragStart={(event) => onDragStart(event, 'actionNode', 'HTTP Request')} 
        draggable
      >
        <div className="node-icon icon-action"><Play size={14} /></div>
        HTTP Request
      </div>
      
      <h4 style={{ marginTop: '20px', marginBottom: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
        Context Studio (Plug & Play)
      </h4>
      
      <div 
        className="draggable-item" 
        onDragStart={(event) => onDragStart(event, 'memoryNode', 'Retrieve Context')} 
        draggable
      >
        <div className="node-icon icon-memory"><Database size={14} /></div>
        Retrieve Context
      </div>
      
      <div 
        className="draggable-item" 
        onDragStart={(event) => onDragStart(event, 'memoryNode', 'Save to Memory')} 
        draggable
      >
        <div className="node-icon icon-memory" style={{ filter: 'hue-rotate(40deg)' }}><Database size={14} /></div>
        Save to Memory
      </div>
      
      <div style={{ marginTop: 'auto', fontSize: '11px', color: 'var(--text-secondary)', textAlign: 'center' }}>
        Drag nodes onto the canvas
      </div>
    </aside>
  );
}

// StatisticsPanel.js
import * as React from 'react';
import Box from '@mui/material/Box';
import PanelOne from './PanelOne';
import PanelTwo from './PanelTwo';

export default function StatisticsPanel() {
  const [showSecondPanel, setShowSecondPanel] = React.useState(false);

  const togglePanel = () => {
    setShowSecondPanel(prev => !prev);
  };

  return (
    <Box sx={{ backgroundColor: '#1C2526', minWidth: 400, width: 800, height: 600, padding: 4 }}>
      {showSecondPanel ? <PanelTwo onClick={togglePanel} /> : <PanelOne onClick={togglePanel} />}
    </Box>
  );
}

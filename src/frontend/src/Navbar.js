import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';

export default function Navbar() {

  return (
    <Box sx={{ flexGrow: 1, minHeight: "131px"}}>
      <AppBar sx= {{ backgroundColor: '#2B2B2B', height:"131px"}}>
        <Toolbar>
          <Typography 
            variant="h6" 
            component="div" 
            display="flex" 
            alignItems="center" 
            height="131px" 
            fontSize="36px" 
            color="#C4A15B"  
            justifyContent="center" 
            sx={{ flexGrow: 1, WebkitTextStroke: '1px #EDDC91' }}>
                League of Legends Prediction Tool
          </Typography>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

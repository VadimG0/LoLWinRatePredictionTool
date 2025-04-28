// PanelOne.js
import React from 'react';
import { Box, Typography } from '@mui/material';

export default function PanelOne({ onClick, winRate = 0 }) {
    const winRateColor = winRate >= 50 ? '#2196f3' : '#f44336';
    const displayWinRate = winRate?.toFixed?.(2) ?? '0.00';

    return (
        <Box
            onClick={onClick}
            sx={{
                position: 'relative',
                width: '100%',
                height: '100%',
                borderRadius: 5,
                overflow: 'hidden',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                backgroundImage: 'url(https://img.youtube.com/vi/88Nh8irxfA8/maxresdefault.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundAttachment: 'fixed',
                color: '#fff'
            }}
        >
            <Box sx={{ textAlign: 'center', px: 4 }}>
                <Typography variant="h5" sx={{ color: '#f9f871' }}>Team Win Rate</Typography>
                <Box mt={12} mb={4}>
                    <Typography variant="h2" sx={{ fontWeight: 'bold', color: winRateColor }}>
                        {displayWinRate}%
                    </Typography>
                </Box>
                <Box pt={2}>
                    <Typography>
                        <span style={{ color: '#1976d2' }}>Click</span> to view <span style={{ color: '#f00' }}>Suggestions</span>
                    </Typography>
                </Box>
            </Box>
        </Box>
    );
}
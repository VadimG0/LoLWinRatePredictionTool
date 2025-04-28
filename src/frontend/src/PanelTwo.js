// PanelTwo.js
import React from 'react';
import { Box, Typography, Avatar, Grid } from '@mui/material';

export default function PanelTwo({ onClick, suggestions, selectedChampion, championData, ddragonVersion }) {
    const getChampionIconUrl = (championName) => {
        if (!championName || !championData) return undefined;
        const champ = Object.values(championData).find((c) => c.name === championName);
        if (!champ || !champ.image || !champ.image.full) return undefined;
        return `https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${champ.image.full}`;
    };

    const handleDoubleClick = (e) => {
        e.stopPropagation(); // Prevent triggering the parent onClick
        // You can add additional double-click behavior here if needed
    };

    return (
        <Box
            onClick={onClick}
            onDoubleClick={handleDoubleClick}
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
            <Box sx={{ textAlign: 'center', px: 4, pt: 4 }}>
                <Typography variant="h5" sx={{ color: '#f9f871' }}>Suggested Allies</Typography>
                <Box display="flex" justifyContent="center" mt={2} mb={2}>
                    {selectedChampion ? (
                        <Avatar
                            src={getChampionIconUrl(selectedChampion)}
                            alt={selectedChampion}
                            sx={{ 
                                width: 72, 
                                height: 72, 
                                border: '2px solid #fff',
                                '&:hover': {
                                    transform: 'scale(1.1)',
                                    transition: 'transform 0.2s'
                                }
                            }}
                            onDoubleClick={(e) => {
                                e.stopPropagation();
                                // Trigger the suggestions event again if needed
                                if (selectedChampion) {
                                    window.dispatchEvent(new CustomEvent('openSuggestions', {
                                        detail: {
                                            champion: selectedChampion,
                                            role: 'Unknown', // You might want to pass the actual role
                                            team: 'Unknown'   // You might want to pass the actual team
                                        }
                                    }));
                                }
                            }}
                        />
                    ) : (
                        <Avatar sx={{ width: 64, height: 64, mx: 1, bgcolor: '#444' }} />
                    )}
                </Box>
                <Box mt={2} pt={2}>
                    <Grid container spacing={2} justifyContent="center" mt={1}>
                        {Array.isArray(suggestions) && suggestions.length > 0 ? (
                            suggestions.map((sugg, idx) => {
                                const [name, confidence] = Object.entries(sugg)[0] || ['Unknown', 0];
                                return (
                                    <Grid item key={idx}>
                                        <Box 
                                            display="flex" 
                                            flexDirection="column" 
                                            alignItems="center"
                                            onDoubleClick={(e) => e.stopPropagation()}
                                        >
                                            <Avatar
                                                src={getChampionIconUrl(name)}
                                                alt={name}
                                                sx={{
                                                    bgcolor: '#fff',
                                                    color: '#000',
                                                    width: 56,
                                                    height: 56,
                                                    mb: 1,
                                                    '& img': {
                                                        objectFit: 'cover',
                                                        objectPosition: 'center',
                                                    },
                                                    '&:hover': {
                                                        transform: 'scale(1.1)',
                                                        transition: 'transform 0.2s'
                                                    }
                                                }}
                                            />
                                            <Typography variant="body2" sx={{ color: '#f9f871' }}>{name}</Typography>
                                            <Typography variant="caption" sx={{ color: '#ccc' }}>
                                                {(confidence * 100).toFixed(2)}%
                                            </Typography>
                                        </Box>
                                    </Grid>
                                );
                            })
                        ) : (
                            <Typography variant="body2" sx={{ color: '#f9f871', textAlign: 'center', mt: 2 }}>
                                No suggestions available.
                            </Typography>
                        )}
                    </Grid>
                </Box>
            </Box>
        </Box>
    );
}
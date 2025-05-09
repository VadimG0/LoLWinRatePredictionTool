// StatisticsPanel.js
import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import PanelOne from './PanelOne';
import PanelTwo from './PanelTwo';

export default function StatisticsPanel({ blueTeam, redTeam, winRate = null, suggestions = [] }) {
    const [showSecondPanel, setShowSecondPanel] = useState(false);
    const [selectedChampion, setSelectedChampion] = useState(null);
    const [championData, setChampionData] = useState({});
    const [ddragonVersion, setDdragonVersion] = useState('15.5.1');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const togglePanel = () => {
        if (winRate !== null) {
            setShowSecondPanel(prev => !prev);
        }
    };

    // Fetch champion data on mount
    useEffect(() => {
        const fetchChampionData = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('http://localhost:8000/champions');
                if (!response.ok) throw new Error('Failed to fetch champion data');
                const data = await response.json();
                
                if (data?.data) {
                    setChampionData(data.data);
                    const firstChamp = Object.values(data.data)[0];
                    if (firstChamp?.version) setDdragonVersion(firstChamp.version);
                }
            } catch (err) {
                console.error('Error fetching champion data:', err);
                setError('Failed to load champion data');
            } finally {
                setIsLoading(false);
            }
        };
        fetchChampionData();
    }, []);

    // Handle role-based suggestions
    useEffect(() => {
        const handleRoleSuggestions = async (event) => {
            const { champion, role, team } = event.detail;
            const enemyTeam = team === 'Blue Team' ? redTeam : blueTeam;
            const enemyChampion = enemyTeam[role];

            if (!champion || !enemyChampion) return;

            setIsLoading(true);
            try {
                const response = await fetch('http://localhost:8000/suggest_allies', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        champion: champion.replace(/[^a-zA-Z]/g, ''),
                        enemy_champion: enemyChampion.replace(/[^a-zA-Z]/g, ''),
                        lane: role.toUpperCase(),
                    }),
                });

                if (!response.ok) throw new Error('Failed to fetch suggestions');
                const data = await response.json();
                setSelectedChampion(champion);
                setShowSecondPanel(true);
            } catch (error) {
                console.error('Error fetching role-based suggestions:', error);
                setError('Failed to load suggestions');
            } finally {
                setIsLoading(false);
            }
        };

        window.addEventListener('openSuggestions', handleRoleSuggestions);
        return () => window.removeEventListener('openSuggestions', handleRoleSuggestions);
    }, [blueTeam, redTeam]);

    const renderContent = () => {
        if (isLoading) {
            return (
                <Typography variant="h5" sx={{ color: '#f9f871' }}>
                    Loading...
                </Typography>
            );
        }

        if (error) {
            return (
                <Typography variant="h5" sx={{ color: '#f44336' }}>
                    {error}
                </Typography>
            );
        }

        if (winRate === null) {
            return (
                <Box
                    sx={{
                        background: 'linear-gradient(to bottom, #1a1a1a, #2d2d2d)',
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: 5
                    }}
                >
                    <Typography variant="h5" sx={{ color: '#f9f871' }}>
                        Click "Predict Win Rate" to see results
                    </Typography>
                </Box>
            );
        }

        return showSecondPanel ? (
            <PanelTwo
                onClick={togglePanel}
                suggestions={suggestions}
                selectedChampion={selectedChampion}
                championData={championData}
                ddragonVersion={ddragonVersion}
            />
        ) : (
            <PanelOne onClick={togglePanel} winRate={winRate} />
        );
    };

    return (
        <Box sx={{
            width: 800,
            height: 600,
            padding: 1,
            minWidth: 400,
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'black',
            boxShadow: 3,
            position: 'relative',
        }}>
            {renderContent()}
            
            {isLoading && (
                <Box sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'rgba(0,0,0,0.5)',
                    zIndex: 1
                }}>
                    <Typography variant="h6" color="white">
                        Loading data...
                    </Typography>
                </Box>
            )}
        </Box>
    );
}
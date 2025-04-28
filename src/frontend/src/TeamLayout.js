import * as React from 'react';
import { useState } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import StatisticsPanel from './StatisticsPanel';
import TeamColumn from './TeamColumn';
import ChampionInputForm from './ChampionInputForm';
import Button from '@mui/material/Button';

export default function TeamLayout() {
    const [blueTeam, setBlueTeam] = useState({
        Top: null, Jungle: null, Mid: null, Bottom: null, Support: null
    });
    const [redTeam, setRedTeam] = useState({
        Top: null, Jungle: null, Mid: null, Bottom: null, Support: null
    });
    const [activeTeam, setActiveTeam] = useState(null);
    const [activeRole, setActiveRole] = useState(null);
    const [winRate, setWinRate] = useState(null);
    const [suggestions, setSuggestions] = useState([]);

    const handleChampionSelect = (team, role, champion) => {
        if (team === 'Blue Team') {
            setBlueTeam((prev) => ({ ...prev, [role]: champion }));
        } else {
            setRedTeam((prev) => ({ ...prev, [role]: champion }));
        }
        setActiveTeam(null);
        setActiveRole(null);
    };

    const handleRoleClick = (team, role) => {
        setActiveTeam(team);
        setActiveRole(role);
    };

    const predictWinRate = async () => {
        try {
            const cleanTeam = (team) => {
                const cleaned = {};
                for (const [role, champ] of Object.entries(team || {})) {
                    if (champ) {
                        cleaned[role] = champ.replace(/[^a-zA-Z]/g, '');
                    }
                }
                return cleaned;
            };

            const cleanedBlueTeam = cleanTeam(blueTeam);
            const cleanedRedTeam = cleanTeam(redTeam);

            if (Object.keys(cleanedBlueTeam).length > 0 && Object.keys(cleanedRedTeam).length > 0) {
                console.log('Fetching win rate for:', { blue_team: cleanedBlueTeam, red_team: cleanedRedTeam });
                const response = await fetch('http://localhost:8000/predict_team_win_rate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        blue_team: cleanedBlueTeam,
                        red_team: cleanedRedTeam,
                    }),
                });
                const data = await response.json();
                console.log('Win rate response:', data);
                setWinRate(data.win_rate);
                setSuggestions(data.suggested_allies || []);
            } else {
                console.log('Not enough champions selected to predict win rate.');
            }
        } catch (err) {
            console.error('Error fetching win rate:', err.message);
        }
    };

    return (
        <Box sx={{ padding: 2 }}>
            <Box sx={{ 
                width: '100%', 
                display: 'flex', 
                flexDirection: 'row',
                justifyContent: 'center',
            }}>
                <Box sx={{ 
                    display: 'flex', 
                    position: 'relative',
                    alignItems: 'center',
                    justifyContent: 'center',
                }}>
                    <ChampionInputForm 
                        onChampionSelect={handleChampionSelect}
                        activeTeam={activeTeam}
                        activeRole={activeRole}
                    />
                    <Button
                        variant="contained"
                        sx={{
                            position: 'absolute',
                            zIndex: 1,
                            left: '100%',
                            top: 0,
                            marginLeft: '16px',
                            marginTop: '32px',
                            height: '52px',
                            width: '125px',
                            backgroundColor: '#EDDC91',
                            color: '#2B2B2B',
                            '&:hover': { backgroundColor: '#C4A15B' },
                        }}
                        onClick={predictWinRate}
                    >
                        Predict Win Rate
                    </Button>
                </Box>
            </Box>
            <Stack direction="row" spacing={2} justifyContent="center" alignItems="center" mt={6}>
                <TeamColumn
                    teamName="Blue Team"
                    teamColor="#1F2B44"
                    textColor="#3A9BDC"
                    champions={blueTeam}
                    onRoleClick={handleRoleClick}
                    activeTeam={activeTeam}
                    activeRole={activeRole}
                    blueTeam={blueTeam}
                    redTeam={redTeam}
                />
                <StatisticsPanel 
                    blueTeam={blueTeam} 
                    redTeam={redTeam} 
                    winRate={winRate}
                    suggestions={suggestions}
                />
                <TeamColumn
                    teamName="Red Team"
                    teamColor="#3A1F2E"
                    textColor="#E26565"
                    champions={redTeam}
                    onRoleClick={handleRoleClick}
                    activeTeam={activeTeam}
                    activeRole={activeRole}
                    blueTeam={blueTeam}
                    redTeam={redTeam}
                />
            </Stack>
        </Box>
    );
}
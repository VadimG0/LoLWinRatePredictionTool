import * as React from 'react';
import { useState } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import StatisticsPanel from './StatisticsPanel';
import TeamColumn from './TeamColumn';
import ChampionInputForm from './ChampionInputForm';

export default function TeamLayout() {
    const [blueTeam, setBlueTeam] = useState({
        Top: null, Jungle: null, Mid: null, Bottom: null, Support: null
    });
    const [redTeam, setRedTeam] = useState({
        Top: null, Jungle: null, Mid: null, Bottom: null, Support: null
    });
    const [activeTeam, setActiveTeam] = useState(null);
    const [activeRole, setActiveRole] = useState(null);

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

    return (
        <Box sx={{ backgroundColor: '#1C2526', minHeight: '100vh', padding: 4 }}>
            <Typography
                variant="h4"
                sx={{ color: '#EDDC91', textAlign: 'center', mb: 4, fontWeight: 600 }}
            >
                League of Legends Prediction Tool
            </Typography>
            <ChampionInputForm
                onChampionSelect={handleChampionSelect}
                activeTeam={activeTeam}
                activeRole={activeRole}
            />
            <Stack direction="row" spacing={2} justifyContent="center" alignItems="center" mt={4}>
                <TeamColumn
                    teamName="Blue Team"
                    teamColor="#162341"
                    textColor="#4EC8F0"
                    champions={blueTeam}
                    onRoleClick={handleRoleClick}
                />
                <StatisticsPanel />
                <TeamColumn
                    teamName="Red Team"
                    teamColor="#3A1F2E"
                    textColor="#E26565"
                    champions={redTeam}
                    onRoleClick={handleRoleClick}
                />
            </Stack>
        </Box>
    );
}
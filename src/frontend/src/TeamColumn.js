//TeamColumn.js

import React, { useState, useEffect } from 'react';
import { Box, Stack, Typography, Avatar, Tooltip, CircularProgress } from '@mui/material';

const roles = ['Top', 'Jungle', 'Mid', 'Bottom', 'Support'];

export default function TeamColumn({ teamName, teamColor, textColor, champions, onRoleClick, activeTeam, activeRole, blueTeam, redTeam }) {
    const [championData, setChampionData] = useState({});
    const [ddragonVersion, setDdragonVersion] = useState('15.5.1');
    const [hoveredChampion, setHoveredChampion] = useState(null);
    const [allySuggestions, setAllySuggestions] = useState({});
    const [loading, setLoading] = useState({});

    useEffect(() => {
        fetch('http://localhost:8000/champions')
            .then((response) => response.json())
            .then((data) => {
                if (data && data.data) {
                    setChampionData(data.data);
                    const firstChamp = Object.values(data.data)[0];
                    if (firstChamp && firstChamp.version) {
                        setDdragonVersion(firstChamp.version);
                    }
                }
            })
            .catch((error) => console.error('Error fetching champion data:', error));
    }, []);

    const getChampionIconUrl = (championName) => {
        if (!championName) return undefined;
        const champ = Object.values(championData).find((c) => c.name === championName);
        if (!champ || !champ.image || !champ.image.full) return undefined;
        return `https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${champ.image.full}`;
    };

    // Fetch ally suggestions when hovering over a champion
    const fetchAllySuggestions = async (myChampion, enemyChampion, lane) => {
        if (!myChampion || !enemyChampion) return;

        const cleanedMyChampion = myChampion.replace(/[^a-zA-Z]/g, '');
        const cleanedEnemyChampion = enemyChampion.replace(/[^a-zA-Z]/g, '');
        const cacheKey = `${cleanedMyChampion}-${cleanedEnemyChampion}-${lane}`;

        // Check if already fetched or loading
        if (allySuggestions[cacheKey] || loading[cacheKey]) return;

        setLoading((prev) => ({ ...prev, [cacheKey]: true }));
        try {
            const response = await fetch('http://localhost:8000/suggest_allies', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    champion: cleanedMyChampion,
                    enemy_champion: cleanedEnemyChampion,
                    lane: lane.toUpperCase(),
                }),
            });
            const data = await response.json();
            if (response.ok) {
                setAllySuggestions((prev) => ({ ...prev, [cacheKey]: data }));
            } else {
                console.error('Failed to fetch ally suggestions:', data.detail);
            }
        } catch (err) {
            console.error('Error fetching ally suggestions:', err.message);
        } finally {
            setLoading((prev) => ({ ...prev, [cacheKey]: false }));
        }
    };

    // Log the champions for this team
    useEffect(() => {
        console.log(`${teamName} champions:`, champions);
    }, [teamName, champions]);

    const isActive = (role) => teamName === activeTeam && role === activeRole;

    const handleMouseEnter = (role) => {
        const myChampion = champions[role];
        const enemyTeam = teamName === 'Blue Team' ? redTeam : blueTeam;
        const enemyChampion = enemyTeam ? enemyTeam[role] : null;

        if (myChampion && enemyChampion) {
            setHoveredChampion({ champion: myChampion, role });
            fetchAllySuggestions(myChampion, enemyChampion, role);
        }
    };

    const handleMouseLeave = () => {
        setHoveredChampion(null);
    };

    const renderTooltipContent = (role) => {
        const myChampion = champions[role];
        const enemyTeam = teamName === 'Blue Team' ? redTeam : blueTeam;
        const enemyChampion = enemyTeam ? enemyTeam[role] : null;
        const cacheKey = `${myChampion?.replace(/[^a-zA-Z]/g, '')}-${enemyChampion?.replace(/[^a-zA-Z]/g, '')}-${role}`;

        if (!myChampion || !enemyChampion) {
            return <Typography>No enemy champion in this lane.</Typography>;
        }

        if (loading[cacheKey]) {
            return <CircularProgress size={20} sx={{ color: '#EDDC91' }} />;
        }

        const suggestions = allySuggestions[cacheKey];
        if (!suggestions) {
            return <Typography>No suggestions available.</Typography>;
        }

        return (
            <Box sx={{ p: 1, maxWidth: 300 }}>
                <Typography variant="body2" sx={{ color: '#fff', mb: 1 }}>
                    {suggestions.my_champion} vs {suggestions.enemy_champion} ({suggestions.lane})
                </Typography>
                <Typography variant="body2" sx={{ color: '#fff', mb: 1 }}>
                    Win Rate: {suggestions.win_rate.toFixed(2)}% ({suggestions.matches_analyzed} matches)
                </Typography>
                <Typography variant="body2" sx={{ color: '#EDDC91', mb: 1 }}>
                    Suggested Allies:
                </Typography>
                {suggestions.suggested_allies.length > 0 ? (
                    suggestions.suggested_allies.map((ally, idx) => {
                        const [champ, confidence] = Object.entries(ally)[0];
                        return (
                            <Typography key={idx} variant="body2" sx={{ color: '#fff' }}>
                                {champ}: {(confidence * 100).toFixed(2)}%
                            </Typography>
                        );
                    })
                ) : (
                    <Typography variant="body2" sx={{ color: '#fff' }}>
                        No suggestions available.
                    </Typography>
                )}
            </Box>
        );
    };

    return (
        <Box
            sx={{
                backgroundColor: teamColor,
                paddingTop: 2,
                width: 300,
                height: 600,
            }}
        >
            <Typography
                fontSize="24px"
                sx={{ color: textColor, mb: 4, textAlign: 'center', fontWeight: 600 }}
            >
                {teamName}
            </Typography>
            <Stack
                direction="column"
                sx={{ height: 'calc(100% - 48px)' }}
            >
                {roles.map((role) => (
                    <Tooltip
                        key={role}
                        title={renderTooltipContent(role)}
                        placement={teamName === 'Blue Team' ? 'right' : 'left'}
                        arrow
                        sx={{
                            '& .MuiTooltip-tooltip': {
                                backgroundColor: '#1C2526',
                                border: '1px solid #EDDC91',
                                borderRadius: '4px',
                            },
                            '& .MuiTooltip-arrow': {
                                color: '#EDDC91',
                            },
                        }}
                    >
                        <Stack
                            height="90px"
                            direction="row"
                            alignItems="center"
                            padding={2}
                            spacing={2}
                            onMouseEnter={() => handleMouseEnter(role)}
                            onMouseLeave={handleMouseLeave}
                            onClick={() => onRoleClick(teamName, role)}
                            onDoubleClick={() => {
                            if (champions[role]) {
                                window.dispatchEvent(new CustomEvent('openSuggestions', {
                                detail: {
                                    champion: champions[role],
                                    role: role,
                                    team: teamName,
                                }
                                }));
                            }
                            }}
                            
                            sx={{
                                width: '100%',
                                cursor: 'pointer',
                                justifyContent: teamName === 'Blue Team' ? 'flex-start' : 'flex-end',
                                backgroundImage: `linear-gradient(to left, ${teamColor} 50%, rgba(255, 255, 255, 0.2) 50%)`,
                                backgroundSize: '200% 100%',
                                backgroundPosition: 'right',
                                transition: 'background-position 0.3s ease, background-color 0.1s ease',
                                '&:hover': {
                                    backgroundPosition: 'left',
                                },
                                ...(isActive(role) && {
                                    backgroundPosition: 'left',
                                    backgroundColor: 'rgba(255, 255, 255, 0.3)',
                                }),
                            }}
                        >
                            {teamName === 'Blue Team' ? (
                                <>
                                    <Avatar
                                        sx={{
                                            width: 56,
                                            height: 56,
                                            backgroundColor: champions[role] ? 'transparent' : 'rgba(255,255,255,0.1)',
                                            '& img': {
                                                objectFit: 'cover',
                                                objectPosition: 'center',
                                                transform: 'scale(1.2)',
                                            },
                                        }}
                                        src={getChampionIconUrl(champions[role])}
                                        alt={champions[role] || role}
                                    />
                                    <Typography fontSize="18px" color="#fff">
                                        {champions[role] || role}
                                    </Typography>
                                </>
                            ) : (
                                <>
                                    <Typography fontSize="18px" color="#fff">
                                        {champions[role] || role}
                                    </Typography>
                                    <Avatar
                                        sx={{
                                            width: 56,
                                            height: 56,
                                            backgroundColor: champions[role] ? 'transparent' : 'rgba(255,255,255,0.1)',
                                            '& img': {
                                                objectFit: 'cover',
                                                objectPosition: 'center',
                                                transform: 'scale(1.2)',
                                            },
                                        }}
                                        src={getChampionIconUrl(champions[role])}
                                        alt={champions[role] || role}
                                    />
                                </>
                            )}
                        </Stack>
                    </Tooltip>
                ))}
            </Stack>
        </Box>
    );
}
import React, { useState, useEffect } from 'react';
import { Box, Stack, Typography, Avatar } from '@mui/material';

const roles = ['Top', 'Jungle', 'Mid', 'Bottom', 'Support'];

export default function TeamColumn({ teamName, teamColor, textColor, champions, onRoleClick, activeTeam, activeRole }) {
    const [ddragonVersion, setDdragonVersion] = useState('14.22.1');

    useEffect(() => {
        fetch('https://ddragon.leagueoflegends.com/api/versions.json')
            .then((response) => response.json())
            .then((data) => {
                setDdragonVersion(data[0]);
            })
            .catch((error) => console.error('Error fetching Data Dragon version:', error));
    }, []);

    const getChampionIconUrl = (championName) => {
        if (!championName) return undefined;
        return `https://ddragon.leagueoflegends.com/cdn/${ddragonVersion}/img/champion/${championName}.png`;
    };

    const isActive = (role) => teamName === activeTeam && role === activeRole;

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
                    <Stack
                        height="90px"
                        direction="row"
                        alignItems="center"
                        padding={2}
                        spacing={2}
                        key={role}
                        onClick={() => onRoleClick(teamName, role)}
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
                                backgroundColor: 'rgba(255, 255, 255, 0.2',
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
                ))}
            </Stack>
        </Box>
    );
}
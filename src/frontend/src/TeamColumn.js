import React from 'react';
import { Box, Stack, Typography, Avatar } from '@mui/material';

const roles = ['Top', 'Jungle', 'Mid', 'Bottom', 'Support'];

export default function TeamColumn({ teamName, teamColor, textColor, champions, onRoleClick }) {
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
                sx={{ height: 'calc(100% - 48px)' }} // Adjust for title height
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
                            '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' },
                        }}
                    >
                        {teamName === 'Blue Team' ? (
                            <>
                                <Avatar
                                    sx={{
                                        width: 56,
                                        height: 56,
                                        backgroundColor: champions[role] ? 'transparent' : 'rgba(255,255,255,0.1)',
                                    }}
                                    src={champions[role] ? 'images/zoe_icon.png' : undefined}
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
                                    }}
                                    src={champions[role] ? 'images/zoe_icon.png' : undefined}
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
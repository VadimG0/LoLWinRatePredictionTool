import React from 'react';
import { Box, Stack, Typography, Avatar } from '@mui/material';

const roles = ['Top', 'Jungle', 'Mid', 'Bottom', 'Support'];

export default function TeamColumn({ teamName, teamColor, textColor, champions, onRoleClick }) {
    return (
        <Box
            sx={{
                backgroundColor: teamColor,
                padding: 2,
                borderRadius: 2,
                width: 200,
            }}
        >
            <Typography
                variant="h6"
                sx={{ color: textColor, mb: 2, textAlign: 'center', fontWeight: 600 }}
            >
                {teamName}
            </Typography>
            <Stack spacing={2}>
                {roles.map((role) => (
                    <Stack
                        direction="row"
                        alignItems="center"
                        spacing={1}
                        key={role}
                        onClick={() => onRoleClick(teamName, role)}
                        sx={{ cursor: 'pointer', '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' } }}
                    >
                        <Avatar
                            src={champions[role] ? '/images/zoe_icon.png' : undefined}
                            alt={champions[role] || role}
                        />
                        <Typography color="#fff">{champions[role] || role}</Typography>
                    </Stack>
                ))}
            </Stack>
        </Box>
    );
}
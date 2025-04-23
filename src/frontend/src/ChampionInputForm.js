import * as React from 'react';
import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import Autocomplete from '@mui/material/Autocomplete';
import Avatar from '@mui/material/Avatar';
import Typography from '@mui/material/Typography';

export default function ChampionInputForm({ onChampionSelect, activeTeam, activeRole }) {
    const [selectedChampion, setSelectedChampion] = useState(null);
    const [inputValue, setInputValue] = useState('');
    const [championData, setChampionData] = useState({});
    const [championNames, setChampionNames] = useState([]);
    const [ddragonVersion, setDdragonVersion] = useState('15.5.1');

    useEffect(() => {
        fetch('http://localhost:8000/champions')
            .then((response) => response.json())
            .then((data) => {
                if (data && data.data) {
                    setChampionData(data.data);
                    const names = Object.values(data.data)
                        .map((champ) => champ.name)
                        .sort();
                    setChampionNames(names);
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

    useEffect(() => {
        setSelectedChampion(null);
        setInputValue('');
    }, [activeTeam, activeRole]);

    const handleSubmit = () => {
        if (selectedChampion && activeTeam && activeRole) {
            onChampionSelect(activeTeam, activeRole, selectedChampion);
            console.log(`Selected champion: ${selectedChampion} for ${activeTeam} ${activeRole}`);
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            const matches = championNames.filter((option) =>
                option.toLowerCase().includes(inputValue.toLowerCase())
            );
            if (matches.length > 0) {
                // Prioritize exact match (case-insensitive)
                const exactMatch = matches.find(
                    (option) => option.toLowerCase() === inputValue.toLowerCase()
                );
                const firstMatch = exactMatch || matches[0]; // Fallback to first partial match
                setSelectedChampion(firstMatch);
                setInputValue(firstMatch);
                console.log(`Auto-selected champion: ${firstMatch}`);
                handleSubmit();
            }
        }
    };

    return (
        <Stack direction="row" justifyContent="center" alignItems="center" mt={4} height="52px">
            <Box
                component="form"
                sx={{ '& > :not(style)': { m: 1, width: '50ch' } }}
                noValidate
                autoComplete="off"
                display="flex"
                justifyContent="center"
            >
                <Autocomplete
                    id="champion-search"
                    options={championNames}
                    inputValue={inputValue}
                    onInputChange={(event, newValue) => {
                        setInputValue(newValue);
                        if (!newValue) setSelectedChampion(null);
                    }}
                    onChange={(event, newValue) => {
                        setSelectedChampion(newValue);
                        setInputValue(newValue || '');
                    }}
                    noOptionsText="No champion found"
                    isOptionEqualToValue={(option, value) => option === value}
                    renderOption={(props, option) => (
                        <Box component="li" sx={{ display: 'flex', alignItems: 'center', padding: 1 }} {...props}>
                            <Avatar
                                src={getChampionIconUrl(option)}
                                alt={option}
                                sx={{
                                    width: 32,
                                    height: 32,
                                    mr: 1,
                                    '& img': {
                                        objectFit: 'cover',
                                        objectPosition: 'center',
                                        transform: 'scale(1.2)',
                                    },
                                }}
                            />
                            <Typography variant="body1">{option}</Typography>
                        </Box>
                    )}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="Type champion name..."
                            variant="outlined"
                            onKeyDown={handleKeyDown}
                        />
                    )}
                    filterOptions={(options, { inputValue }) =>
                        inputValue
                            ? options.filter((option) =>
                                  option.toLowerCase().includes(inputValue.toLowerCase())
                              )
                            : options
                    }
                    sx={{
                        '& .MuiOutlinedInput-root': {
                            '&.Mui-focused fieldset': {
                                borderColor: '#EDDC91',
                            },
                            '& .MuiOutlinedInput-input': {
                                color: '#fff',
                            },
                        },
                        '& label.Mui-focused': {
                            color: '#EDDC91',
                        },
                        '& label': {
                            color: '#AAAAAA',
                        },
                        '& .MuiAutocomplete-popupIndicator': {
                            color: 'white',
                        },
                        '& .MuiAutocomplete-popupIndicatorOpen': {
                            color: '#EDDC91',
                        },
                        '& .MuiAutocomplete-clearIndicator': {
                            color: '#EDDC91',
                        },
                        backgroundColor: '#2B2B2B',
                    }}
                />
            </Box>
            <Button
                variant="contained"
                sx={{ height: "100%", backgroundColor: '#EDDC91', color: '#2B2B2B', '&:hover': { backgroundColor: '#C4A15B' } }}
                onClick={handleSubmit}
            >
                <SendRoundedIcon />
            </Button>
        </Stack>
    );
}
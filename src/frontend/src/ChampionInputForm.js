import * as React from 'react';
import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import Autocomplete from '@mui/material/Autocomplete';

const championNames = [
    "Aatrox", "Ahri", "Akali", "Akshan", "Alistar", "Amumu", "Anivia", "Annie",
    "Aphelios", "Ashe", "Aurelion Sol", "Azir", "Bard", "Blitzcrank", "Brand",
    "Braum", "Caitlyn", "Camille", "Cassiopeia", "Cho'Gath", "Corki", "Darius",
    "Diana", "Dr. Mundo", "Draven", "Ekko", "Elise", "Evelynn", "Ezreal",
    "Fiddlesticks", "Fiora", "Fizz", "Galio", "Gangplank", "Garen", "Gnar",
    "Gragas", "Graves", "Hecarim", "Heimerdinger", "Illaoi", "Irelia", "Ivern",
    "Janna", "Jarvan IV", "Jax", "Jayce", "Jhin", "Jinx", "Kai'Sa", "Kalista",
    "Karma", "Karthus", "Kassadin", "Katarina", "Kayle", "Kayn", "Kennen",
    "Kha'Zix", "Kindred", "Kled", "Kog'Maw", "LeBlanc", "Lee Sin", "Leona",
    "Lillia", "Lissandra", "Lucian", "Lulu", "Lux", "Malphite", "Malzahar",
    "Maokai", "Master Yi", "Miss Fortune", "Mordekaiser", "Morgana", "Nami",
    "Nasus", "Nautilus", "Neeko", "Nidalee", "Nocturne", "Nunu & Willump",
    "Olaf", "Orianna", "Ornn", "Pantheon", "Poppy", "Pyke", "Qiyana", "Quinn",
    "Rakan", "Rammus", "Rek'Sai", "Rell", "Renata Glasc", "Renekton", "Rengar",
    "Riven", "Rumble", "Ryze", "Samira", "Sejuani", "Senna", "Seraphine",
    "Sett", "Shaco", "Shen", "Shyvana", "Singed", "Sion", "Sivir", "Skarner",
    "Sona", "Soraka", "Swain", "Sylas", "Syndra", "Tahm Kench", "Taliyah",
    "Talon", "Taric", "Teemo", "Thresh", "Tristana", "Trundle", "Tryndamere",
    "Twisted Fate", "Twitch", "Udyr", "Urgot", "Varus", "Vayne", "Veigar",
    "Vel'Koz", "Vex", "Vi", "Viktor", "Vladimir", "Volibear", "Warwick", "Wukong",
    "Xayah", "Xerath", "Xin Zhao", "Yasuo", "Yone", "Yorick", "Yuumi", "Zac",
    "Zed", "Zeri", "Ziggs", "Zilean", "Zoe", "Zyra"
]

export default function ChampionInputForm({ onChampionSelect, activeTeam, activeRole }) {
    const [selectedChampion, setSelectedChampion] = useState(null);
    const [inputValue, setInputValue] = useState('');

    const handleSubmit = () => {
        if (selectedChampion && activeTeam && activeRole) {
            console.log(`Selected champion: ${selectedChampion}`);
            // Placeholder for backend call
            onChampionSelect( activeTeam, activeRole, selectedChampion )
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            const matches = championNames.filter((option) =>
                option.toLowerCase().includes(inputValue.toLowerCase())
            );
            if (matches.length > 0) {
                const firstMatch = matches[0];
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
                        if (!newValue) setSelectedChampion(null); // Reset if input cleared
                    }}
                    onChange={(event, newValue) => {
                        setSelectedChampion(newValue);
                        setInputValue(newValue || '');
                    }}
                    noOptionsText="No champion found"
                    isOptionEqualToValue={(option, value) => option === value}
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
                        // change popup Indicator to #EDDC91 when open
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
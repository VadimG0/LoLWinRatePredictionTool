import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme';

import Navbar from './Navbar';
import App from './App';
import ChampionInputForm from './ChampionInputForm';
import TeamLayout from './TeamLayout';



const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Navbar />
      <TeamLayout />
    </ThemeProvider>
  </React.StrictMode>
);


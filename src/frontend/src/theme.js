import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  typography: {
    fontFamily: 'Poppins, Roboto, sans-serif',
  },
  palette: {
    // Optional: add your brand colors here
    background: {
      default: '#1A1A1A',
    },
  },
});

export default theme;

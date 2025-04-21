import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  typography: {
    fontFamily: 'Poppins, Roboto, sans-serif',
  },
  palette: {
    // Optional: add your brand colors here
    background: {
      default: 'white',
    },
  },
});

export default theme;

// Material UI Components
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Paper,
} from '@mui/material';
// Icons
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import CodeOutlinedIcon from '@mui/icons-material/CodeOutlined';
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined';
// Navigation
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Analyze',
      description:
        'Upload a dataset and write an SQL query with aggregate constraints. The system analyzes your input and checks for violations.',
      Icon: SearchOutlinedIcon,
    },
    {
      title: 'Repair',
      description:
        'Behind the scenes, advanced repair algorithms like Full Filtering and Range Pruning automatically generate an equivalent query that satisfies the constraint.',
      Icon: CodeOutlinedIcon,
    },
    {
      title: 'Understand',
      description:
        'See visual difference between the original and repaired queries. Use graphs, metrics, and explanations to understand what changed—and why it matters.',
      Icon: LightbulbOutlinedIcon,
    },
  ];

  const handleGetStarted = () => {
    // navigate('/editor');
    navigate('/input');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 2}}>
      {/* Hero Section */}
      <Box textAlign="center" mb={2}>
        <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
          Understand and Repair SQL Queries with Confidence
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={3} maxWidth="md" mx="auto">
          Query Repair System is an educational tool designed to help you learn how aggregate constraints affect SQL Queries — 
          and how they can be repaired using algorithms like Full Filtering and Range Pruning. 
          Upload a dataset, write query, define constraints, and visually explore how query repairs happen.
        </Typography>
        <Button variant="contained" size="large" onClick={handleGetStarted}>
          Get started
        </Button>
      </Box>

      {/* How it works Section */}
      <Typography
        variant="h4"
        component="h2"
        align="center"
        gutterBottom
        fontWeight="bold"
      >
        How it works
      </Typography>

      <Grid container spacing={4}>
        {features.map((feature) => (
          <Grid size={{xs:12, md:4}} key={feature.title}>
            <Paper elevation={3} sx={{ p: 3, pb: 0, height: '100%' }}>
              <Box display="flex" alignItems="center" mb={2}>
                <feature.Icon color="primary" sx={{ fontSize: 32, mr: 1 }} />
                <Typography variant="h6" fontWeight="medium">
                  {feature.title}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {feature.description}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

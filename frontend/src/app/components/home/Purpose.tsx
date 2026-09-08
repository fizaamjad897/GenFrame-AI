'use client';

import { Box, Typography, Container, Grid, Paper } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SpeedIcon from '@mui/icons-material/Speed';
import AccessibilityIcon from '@mui/icons-material/Accessibility';

export default function PurposeSection() {
    const features = [
        {
            icon: <AutoAwesomeIcon sx={{ fontSize: 40, color: 'rgba(139, 92, 246, 1)' }} />,
            title: "AI-Powered Precision",
            desc: "Our advanced neural engines transform raw concepts into studio-quality media assets with surgical precision."
        },
        {
            icon: <SpeedIcon sx={{ fontSize: 40, color: 'rgba(139, 92, 246, 1)' }} />,
            title: "Unmatched Velocity",
            desc: "Bypass manual design cycles. Generate, iterate, and deploy professional visuals at the speed of thought."
        },
        {
            icon: <AccessibilityIcon sx={{ fontSize: 40, color: 'rgba(139, 92, 246, 1)' }} />,
            title: "Inclusive Design",
            desc: "Every asset is automatically optimized for ADA compliance, ensuring your message reaches everyone."
        }
    ];

    return (
        <Box sx={{ py: 15, bgcolor: '#ffffff', borderTop: '1px solid #FFFFFF' }}>
            <Container maxWidth="lg">
                <Box textAlign="center" mb={10}>
                    <Typography
                        variant="overline"
                        sx={{ fontWeight: 600, color: 'rgba(139, 92, 246, 1)', letterSpacing: '0.2em' }}
                    >
                        OUR MISSION
                    </Typography>
                    <Typography
                        variant="h3"
                        sx={{
                            fontWeight: 500,
                            color: '#111827',
                            mt: 2,
                            mb: 3,
                            letterSpacing: '-0.02em',
                            fontSize: { xs: '32px', md: '46px' }
                        }}
                    >
                        Democratizing Professional Design.
                    </Typography>
                    <Typography
                        variant="h6"
                        sx={{ color: '#6B7280', maxWidth: '700px', mx: 'auto', fontWeight: 400, lineHeight: 1.6, fontSize: { xs: '18px', md: '18px' } }}
                    >
                        Recreative AI bridges the gap between complex AI capabilities and intuitive creative control, empowering every business to tell their story visually.
                    </Typography>
                </Box>

                <Grid container spacing={4}>
                    {features.map((f, i) => (
                        <Grid size={{ xs: 12, md: 4 }} key={i}>
                            <Paper
                                elevation={0}
                                sx={{
                                    p: 5,
                                    height: '100%',
                                    borderRadius: '24px',
                                    border: '1px solid #FFFFFF',
                                    transition: 'all 0.3s ease',
                                    '&:hover': {
                                        transform: 'translateY(-8px)',
                                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.05)',
                                        borderColor: 'rgba(139, 92, 246, 0.2)'
                                    }
                                }}
                            >
                                <Box sx={{ mb: 3 }}>
                                    {f.icon}
                                </Box>
                                <Typography variant="h5" sx={{ fontWeight: 600, mb: 2, color: '#111827' }}>
                                    {f.title}
                                </Typography>
                                <Typography sx={{ color: '#6B7280', lineHeight: 1.7, fontSize: '0.95rem' }}>
                                    {f.desc}
                                </Typography>
                            </Paper>
                        </Grid>
                    ))}
                </Grid>
            </Container>
        </Box>
    );
}

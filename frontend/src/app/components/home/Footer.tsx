'use client';

import { Box, Typography, Container } from '@mui/material';

export default function Footer() {
    return (
        <Box sx={{ py: 6, borderTop: '1px solid #e5e7eb', mt: 8 }}>
            <Container maxWidth="lg">
                <Typography variant="body2" color="text.secondary" align="center">
                    © {new Date().getFullYear()} GenFrame. All rights reserved.
                </Typography>
            </Container>
        </Box>
    );
}

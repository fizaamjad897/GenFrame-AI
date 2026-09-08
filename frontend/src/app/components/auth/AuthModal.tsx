'use client';

import { Modal, Box, Typography, Button } from '@mui/material';
import { useRouter } from 'next/navigation';

export default function AuthModal({ open, onClose }: { open: boolean, onClose: () => void }) {
    const router = useRouter();

    return (
        <Modal open={open} onClose={onClose}>
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: 400,
                bgcolor: '#FFFFFF',
                borderRadius: '18px',
                border: '1px solid #E5E7EB',
                boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                p: 4,
                textAlign: 'center'
            }}>
                <Typography variant="h5" sx={{ mb: 2, fontWeight: 500, color: '#111827' }}>
                    Account Required
                </Typography>
                <Typography sx={{ mb: 4, color: '#6B7280' }}>
                    Please log in or sign up to continue with your purchase.
                </Typography>
                <Button
                    fullWidth
                    variant="contained"
                    sx={{ mb: 2, bgcolor: '#8B5CF6', color: '#FFFFFF', borderRadius: '18px', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)', fontWeight: 500, textTransform: 'none', '&:hover': { bgcolor: '#8B5CF6', filter: 'brightness(0.92)', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' } }}
                    onClick={() => router.push('/auth')}
                >
                    Go to Login/Signup
                </Button>
                <Button
                    fullWidth
                    variant="outlined"
                    sx={{ borderRadius: '18px', borderColor: '#E5E7EB', borderStyle: 'solid', color: '#111827', textTransform: 'none', '&:hover': { borderColor: '#8B5CF6', bgcolor: 'rgba(139,92,246,0.04)' } }}
                    onClick={onClose}
                >
                    Cancel
                </Button>
            </Box>
        </Modal>
    );
}

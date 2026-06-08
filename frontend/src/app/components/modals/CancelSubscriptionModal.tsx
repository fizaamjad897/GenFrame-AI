"use client";

import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Typography,
    Box,
    Alert,
    CircularProgress,
} from '@mui/material';
import {
    Warning as WarningIcon,
} from '@mui/icons-material';

interface CancelSubscriptionModalProps {
    open: boolean;
    onClose: () => void;
    onConfirm: () => Promise<void>;
    planName: string;
    loading?: boolean;
}

const CancelSubscriptionModal: React.FC<CancelSubscriptionModalProps> = ({
    open,
    onClose,
    onConfirm,
    planName,
    loading = false,
}) => {
    const [isProcessing, setIsProcessing] = React.useState(false);

    const handleConfirm = async () => {
        setIsProcessing(true);
        try {
            await onConfirm();
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <Dialog
            open={open}
            onClose={loading || isProcessing ? undefined : onClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                sx: {
                    borderRadius: '24px',
                    p: 2,
                }
            }}
        >
            <DialogTitle sx={{ pb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                        sx={{
                            width: 48,
                            height: 48,
                            borderRadius: '12px',
                            bgcolor: 'rgba(239, 68, 68, 0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <WarningIcon sx={{ fontSize: 28, color: '#ef4444' }} />
                    </Box>
                    <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '20px', color: '#111827' }}>
                            Cancel Your Plan?
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '14px' }}>
                            This action will end your subscription
                        </Typography>
                    </Box>
                </Box>
            </DialogTitle>

            <DialogContent>
                <Alert severity="warning" sx={{ mb: 2 }}>
                    <Typography sx={{ fontSize: '14px', fontWeight: 600, mb: 1 }}>
                        What happens when you cancel:
                    </Typography>
                    <Box component="ul" sx={{ m: 0, pl: 2, fontSize: '13px' }}>
                        <li>Your <strong>{planName}</strong> plan will end immediately</li>
                        <li>You'll lose all monthly credits</li>
                        <li>Any add-on credits you purchased will remain</li>
                        <li>You can subscribe to a new plan anytime</li>
                    </Box>
                </Alert>

                <Typography sx={{ fontSize: '14px', color: '#6b7280' }}>
                    Are you sure you want to cancel? This cannot be undone.
                </Typography>
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
                <Button
                    onClick={onClose}
                    disabled={loading || isProcessing}
                    sx={{
                        textTransform: 'none',
                        fontWeight: 600,
                        color: '#6b7280',
                        px: 3,
                        '&:hover': {
                            bgcolor: '#f3f4f6',
                        },
                    }}
                >
                    Keep My Plan
                </Button>
                <Button
                    onClick={handleConfirm}
                    disabled={loading || isProcessing}
                    variant="contained"
                    color="error"
                    startIcon={isProcessing ? <CircularProgress size={16} color="inherit" /> : null}
                    sx={{
                        textTransform: 'none',
                        fontWeight: 600,
                        px: 3,
                        borderRadius: '10px',
                    }}
                >
                    {isProcessing ? 'Cancelling...' : 'Yes, Cancel Plan'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default CancelSubscriptionModal;

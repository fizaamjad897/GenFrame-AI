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
                    borderRadius: '18px',
                    border: '1px solid #E5E7EB',
                    boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                    bgcolor: '#FFFFFF',
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
                            borderRadius: '18px',
                            border: '1px solid rgba(180, 72, 47, 0.4)',
                            bgcolor: 'transparent',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <WarningIcon sx={{ fontSize: 28, color: '#EF4444' }} />
                    </Box>
                    <Box>
                        <Typography variant="h6" sx={{ fontWeight: 500, fontSize: '20px', color: '#111827' }}>
                            Cancel Your Plan?
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#6B7280', fontSize: '14px' }}>
                            This action will end your subscription
                        </Typography>
                    </Box>
                </Box>
            </DialogTitle>

            <DialogContent>
                <Alert severity="warning" sx={{ mb: 2, borderRadius: '18px' }}>
                    <Typography sx={{ fontSize: '14px', fontWeight: 500, mb: 1 }}>
                        What happens when you cancel:
                    </Typography>
                    <Box component="ul" sx={{ m: 0, pl: 2, fontSize: '13px' }}>
                        <li>Your <strong>{planName}</strong> plan will end immediately</li>
                        <li>You'll lose all monthly credits</li>
                        <li>Any add-on credits you purchased will remain</li>
                        <li>You can subscribe to a new plan anytime</li>
                    </Box>
                </Alert>

                <Typography sx={{ fontSize: '14px', color: '#6B7280' }}>
                    Are you sure you want to cancel? This cannot be undone.
                </Typography>
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
                <Button
                    onClick={onClose}
                    disabled={loading || isProcessing}
                    sx={{
                        textTransform: 'none',
                        fontWeight: 500,
                        color: '#6B7280',
                        px: 3,
                        '&:hover': {
                            bgcolor: '#FFFFFF',
                        },
                    }}
                >
                    Keep My Plan
                </Button>
                <Button
                    onClick={handleConfirm}
                    disabled={loading || isProcessing}
                    variant="contained"
                    startIcon={isProcessing ? <CircularProgress size={16} color="inherit" /> : null}
                    sx={{
                        textTransform: 'none',
                        fontWeight: 500,
                        px: 3,
                        borderRadius: '18px',
                        boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                        bgcolor: '#EF4444',
                        color: '#FFFFFF',
                        '&:hover': {
                            bgcolor: '#EF4444',
                            filter: 'brightness(0.9)',
                            boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                        },
                    }}
                >
                    {isProcessing ? 'Cancelling...' : 'Yes, Cancel Plan'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default CancelSubscriptionModal;

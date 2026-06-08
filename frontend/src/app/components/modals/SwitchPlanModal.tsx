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
} from '@mui/material';
import {
    SwapHoriz as SwapIcon,
} from '@mui/icons-material';

interface SwitchPlanModalProps {
    open: boolean;
    onClose: () => void;
    onCancel: () => void;
    currentPlan: string;
    newPlan: string;
}

const SwitchPlanModal: React.FC<SwitchPlanModalProps> = ({
    open,
    onClose,
    onCancel,
    currentPlan,
    newPlan,
}) => {
    return (
        <Dialog
            open={open}
            onClose={onClose}
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
                            bgcolor: 'rgba(59, 130, 246, 0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <SwapIcon sx={{ fontSize: 28, color: '#3b82f6' }} />
                    </Box>
                    <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600, fontSize: '20px', color: '#111827' }}>
                            Switch Your Plan
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#6b7280', fontSize: '14px' }}>
                            You already have an active plan
                        </Typography>
                    </Box>
                </Box>
            </DialogTitle>

            <DialogContent>
                <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography sx={{ fontSize: '14px', mb: 1 }}>
                        You're currently on the <strong>{currentPlan}</strong> plan.
                    </Typography>
                    <Typography sx={{ fontSize: '13px' }}>
                        To switch to <strong>{newPlan}</strong>, you need to cancel your current plan first.
                    </Typography>
                </Alert>

                <Typography sx={{ fontSize: '14px', color: '#6b7280', mb: 2 }}>
                    Would you like to:
                </Typography>

                <Box component="ul" sx={{ m: 0, pl: 2, fontSize: '14px', color: '#111827' }}>
                    <li style={{ marginBottom: '8px' }}>
                        <strong>Cancel {currentPlan}</strong> and then subscribe to {newPlan}
                    </li>
                    <li>
                        Or <strong>keep your current plan</strong> and stay on {currentPlan}
                    </li>
                </Box>
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
                <Button
                    onClick={onClose}
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
                    Keep Current Plan
                </Button>
                <Button
                    onClick={onCancel}
                    variant="contained"
                    sx={{
                        textTransform: 'none',
                        fontWeight: 600,
                        px: 3,
                        borderRadius: '10px',
                        bgcolor: '#3b82f6',
                        '&:hover': {
                            bgcolor: '#2563eb',
                        },
                    }}
                >
                    Cancel {currentPlan} First
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default SwitchPlanModal;

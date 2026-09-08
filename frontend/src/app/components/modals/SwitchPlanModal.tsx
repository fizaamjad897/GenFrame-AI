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
                            border: '1px solid rgba(139, 92, 246, 0.4)',
                            bgcolor: 'transparent',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <SwapIcon sx={{ fontSize: 28, color: '#8B5CF6' }} />
                    </Box>
                    <Box>
                        <Typography variant="h6" sx={{ fontWeight: 500, fontSize: '20px', color: '#111827' }}>
                            Switch Your Plan
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#6B7280', fontSize: '14px' }}>
                            You already have an active plan
                        </Typography>
                    </Box>
                </Box>
            </DialogTitle>

            <DialogContent>
                <Alert severity="info" sx={{ mb: 2, borderRadius: '18px' }}>
                    <Typography sx={{ fontSize: '14px', mb: 1 }}>
                        You're currently on the <strong>{currentPlan}</strong> plan.
                    </Typography>
                    <Typography sx={{ fontSize: '13px' }}>
                        To switch to <strong>{newPlan}</strong>, you need to cancel your current plan first.
                    </Typography>
                </Alert>

                <Typography sx={{ fontSize: '14px', color: '#6B7280', mb: 2 }}>
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
                        fontWeight: 500,
                        color: '#6B7280',
                        px: 3,
                        '&:hover': {
                            bgcolor: '#FFFFFF',
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
                        fontWeight: 500,
                        px: 3,
                        borderRadius: '18px',
                        boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                        bgcolor: '#8B5CF6',
                        color: '#FFFFFF',
                        '&:hover': {
                            bgcolor: '#8B5CF6',
                            filter: 'brightness(0.92)',
                            boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
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

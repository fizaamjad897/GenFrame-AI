"use client";

import { Box, Typography, LinearProgress, Paper, Chip, Button } from '@mui/material';
import { useRouter } from 'next/navigation';
import { useUser } from '@/app/context/AuthContext';
import type { EngineType } from '@/types/billing';
import { getPlanLabel, hasEngineActiveSubscription, getEnginePlan } from '@/types/billing';

const UsageDisplay = ({ horizontal = false, engineType: propEngineType }: { horizontal?: boolean, engineType?: EngineType }) => {
    const { user } = useUser();
    const router = useRouter();

    if (!user) return null;

    const engineType = propEngineType || (user.engineType as EngineType) || 'transformation';
    const engineInfo = user.engine_data?.[engineType];
    const isPostpaid = Boolean((user as any).is_postpaid);
    // Check if THIS SPECIFIC ENGINE has an active subscription
    const subscriptionActive = hasEngineActiveSubscription(user, engineType);
    const enginePlan = getEnginePlan(user, engineType);
    const plan = subscriptionActive ? getPlanLabel(enginePlan) : 'No active subscription';

    // Priority: engine-specific credits → top-level credits
    const engineCredits = engineInfo?.credits || user.credits;

    // Unified Credits: Sum of monthly and add-on usage
    const totalUsed = (engineCredits?.monthly_units_used || 0) + (engineCredits?.addon_units_used || 0);
    const totalMax = (engineCredits?.monthly_units_max || 0) + (engineCredits?.addon_units_max || 0);

    // Remaining credits: monthly (0 if inactive) + addons
    const monthlyRemaining = subscriptionActive
        ? Math.max(0, (engineCredits?.monthly_units_max || 0) - (engineCredits?.monthly_units_used || 0))
        : 0;
    const addonRemaining = Math.max(0, (engineCredits?.addon_units_max || 0) - (engineCredits?.addon_units_used || 0));
    const remainingUnits = monthlyRemaining + addonRemaining;

    const usagePercent = totalMax > 0 ? (totalUsed / totalMax) * 100 : 0;
    const isOverage = totalUsed > totalMax;

    const getProgressColor = () => {
        if (isOverage) return 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
        return 'rgba(3, 105, 161, 1)';
    };

    const getPlanBadgeColor = () => {
        if (isOverage) return { bg: 'rgba(239, 68, 68, 0.08)', color: '#ef4444', border: 'rgba(239, 68, 68, 0.15)' };
        return { bg: 'rgba(3, 105, 161, 0.05)', color: 'rgba(3, 105, 161, 1)', border: 'rgba(3, 105, 161, 0.1)' };
    };

    const badgeColors = getPlanBadgeColor();

    if (horizontal && isPostpaid) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    px: 2,
                    py: 1.5,
                    bgcolor: 'rgba(255, 255, 255, 0.4)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(3, 105, 161, 0.08)',
                    borderRadius: '12px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                    transition: 'all 0.2s ease-in-out',
                    height: '100%',
                    cursor: 'pointer',
                    '&:hover': {
                        transform: 'translateY(-2px)',
                        bgcolor: 'rgba(255, 255, 255, 0.7)',
                        borderColor: 'rgba(3, 105, 161, 0.3)',
                    }
                }}
                onClick={() => router.push('/billing')}
            >
                <Box
                    sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '10px',
                        bgcolor: 'rgba(3, 105, 161, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'rgba(3, 105, 161, 1)',
                        flexShrink: 0,
                        border: '1px solid rgba(3, 105, 161, 0.1)',
                    }}
                >
                    <Typography sx={{ fontSize: '10px', fontWeight: 800 }}>PAYG</Typography>
                </Box>
                <Box sx={{ flex: 1 }}>
                    <Typography sx={{ fontSize: '9px', fontWeight: 700, color: 'rgba(3, 105, 161, 0.6)', textTransform: 'uppercase', letterSpacing: '0.05em', mb: 0.2 }}>
                        Credit Usage
                    </Typography>
                    <Typography sx={{ fontSize: '13px', fontWeight: 600, color: '#111827', lineHeight: 1.2 }}>
                        {totalUsed.toLocaleString()} used
                    </Typography>
                    <Typography sx={{ fontSize: '11px', color: '#6b7280', fontWeight: 500, mt: 0.2 }}>
                        Pay as you go
                    </Typography>
                </Box>
            </Box>
        );
    }

    if (horizontal) {
        return (
            <>
                {/* Legacy Horizontal Version - Commented Out
                <Paper
                    elevation={0}
                    sx={{
                        p: { xs: 1.5, md: '20px 32px' },
                        borderRadius: '20px',
                        border: '1px solid rgba(3, 105, 161, 0.08)',
                        bgcolor: 'rgba(255, 255, 255, 0.8)',
                        backdropFilter: 'blur(20px)',
                        mb: 3,
                        boxShadow: '0 4px 12px rgba(3, 105, 161, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 3,
                        flexWrap: 'wrap',
                        position: 'relative',
                        overflow: 'hidden',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                            boxShadow: '0 24px 48px -12px rgba(3, 105, 161, 0.12)',
                        }
                    }}
                >
                    <Box sx={{
                        position: 'absolute',
                        top: 0,
                        right: 0,
                        width: '150px',
                        height: '150px',
                        background: 'radial-gradient(circle, rgba(3, 105, 161, 0.03) 0%, transparent 70%)',
                        zIndex: 0,
                    }} />

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, position: 'relative', zIndex: 1 }}>
                        <Chip
                            label={plan.toUpperCase()}
                            size="medium"
                            sx={{
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                fontSize: '10px',
                                bgcolor: badgeColors.bg,
                                color: badgeColors.color,
                                borderRadius: '10px',
                                border: `1px solid ${badgeColors.border}`,
                                height: '28px',
                                px: 1.5,
                            }}
                        />
                        <Typography variant="body2" sx={{ fontWeight: 600, color: '#111827', whiteSpace: 'nowrap', fontSize: '13px' }}>
                            {totalUsed.toLocaleString()} <Box component="span" sx={{ color: '#9ca3af', fontWeight: 500 }}>/ {totalMax.toLocaleString()} credits</Box>
                        </Typography>
                    </Box>

                    <Box sx={{ flex: 1, minWidth: '200px', position: 'relative', zIndex: 1 }}>
                        <LinearProgress
                            variant="determinate"
                            value={Math.min(usagePercent, 100)}
                            sx={{
                                height: 8,
                                borderRadius: 4,
                                bgcolor: '#f3f4f6',
                                '& .MuiLinearProgress-bar': {
                                    borderRadius: 4,
                                    background: getProgressColor(),
                                    transition: 'all 0.5s ease',
                                }
                            }}
                        />
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, position: 'relative', zIndex: 1 }}>
                        <Typography
                            variant="caption"
                            sx={{
                                color: isOverage ? '#ef4444' : '#6b7280',
                                fontWeight: 500,
                                display: { xs: 'none', md: 'block' },
                                fontSize: '13px',
                            }}
                        >
                            {isOverage ? '⚠️ Limit Reached' : `${remainingUnits.toLocaleString()} available`}
                        </Typography>
                        <Button
                            size="small"
                            onClick={() => router.push('/pricing')}
                            sx={{
                                textTransform: 'none',
                                color: 'rgba(3, 105, 161,1)',
                                fontWeight: 600,
                                fontSize: '12px',
                                minWidth: 'auto',
                                p: '4px 12px',
                                borderRadius: '6px',
                                bgcolor: 'rgba(3, 105, 161,0.05)',
                                border: '1px solid rgba(3, 105, 161,0.1)',
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    bgcolor: 'rgba(3, 105, 161,0.1)',
                                }
                            }}
                        >
                            Get More
                        </Button>
                    </Box>
                </Paper>
                */}

                {/* Compact Card Layout (Matches Hero Banner Style) */}
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1.5,
                        px: 2,
                        py: 1.5,
                        bgcolor: 'rgba(255, 255, 255, 0.4)',
                        backdropFilter: 'blur(12px)',
                        border: '1px solid rgba(3, 105, 161, 0.08)',
                        borderRadius: '12px',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                        transition: 'all 0.2s ease-in-out',
                        cursor: 'pointer',
                        height: '100%',
                        zIndex: 10,
                        position: 'relative',
                        '&:hover': {
                            transform: 'translateY(-2px)',
                            bgcolor: 'rgba(255, 255, 255, 0.7)',
                            borderColor: 'rgba(3, 105, 161, 0.3)',
                        }
                    }}
                    onClick={() => router.push('/pricing')}
                >
                    <Box
                        sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '10px',
                            bgcolor: badgeColors.bg,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: badgeColors.color,
                            flexShrink: 0,
                            border: `1px solid ${badgeColors.border}`,
                            overflow: 'hidden',
                            position: 'relative'
                        }}
                    >
                        <Box sx={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            right: 0,
                            height: `${Math.min(usagePercent, 100)}%`,
                            opacity: 0.2,
                            background: getProgressColor(),
                            transition: 'height 0.5s ease'
                        }} />
                        <Typography sx={{ fontSize: '10px', fontWeight: 800, zIndex: 1 }}>{Math.round(usagePercent)}%</Typography>
                    </Box>
                    <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.2 }}>
                            <Typography
                                sx={{
                                    fontSize: '9px',
                                    fontWeight: 700,
                                    color: 'rgba(3, 105, 161, 0.6)',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em',
                                }}
                            >
                                Credit Usage
                            </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.5 }}>
                            <Typography
                                sx={{
                                    fontSize: '13px',
                                    fontWeight: 600,
                                    color: '#111827',
                                    lineHeight: 1.2,
                                }}
                            >
                                {totalUsed.toLocaleString()}
                            </Typography>
                            <Typography sx={{ fontSize: '11px', color: '#9ca3af', fontWeight: 500 }}>
                                / {totalMax.toLocaleString()}
                            </Typography>
                        </Box>
                        
                        <Typography
                            sx={{
                                fontSize: '11px',
                                color: isOverage ? '#ef4444' : '#6b7280',
                                fontWeight: 500,
                                mt: 0.2
                            }}
                        >
                            {isPostpaid ? 'Pay as you go' : (isOverage ? '⚠️ Limit Reached' : `${remainingUnits.toLocaleString()} available`)}
                        </Typography>

                        {isOverage && (
                            <Typography 
                                variant="caption" 
                                sx={{ 
                                    color: '#ef4444', 
                                    fontWeight: 600, 
                                    display: 'block', 
                                    fontSize: '10px',
                                    mt: 0.5,
                                    bgcolor: 'rgba(239, 68, 68, 0.05)',
                                    p: 0.5,
                                    borderRadius: '4px',
                                    border: '1px dashed rgba(239, 68, 68, 0.2)',
                                    lineHeight: 1.1
                                }}
                            >
                                Capacity reached. Overage: ${engineCredits?.overageRate || 0.19}/credit
                            </Typography>
                        )}
                    </Box>
                </Box>
            </>
        );
    }

    return (
        /* Original Vertical / Standalone Layout - Commented Out
        <Paper
            elevation={0}
            sx={{
                p: 3,
                borderRadius: '16px',
                border: '1px solid rgba(3, 105, 161, 0.08)',
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                backdropFilter: 'blur(20px)',
                mb: 2.5,
                boxShadow: '0 4px 12px rgba(0,0,0,0.02)',
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
            }}
        >
            <Box sx={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: '120px',
                height: '120px',
                background: 'radial-gradient(circle, rgba(3, 105, 161, 0.03) 0%, transparent 70%)',
                zIndex: 0,
            }} />

            <Box sx={{ position: 'relative', zIndex: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                    <Box>
                        <Typography variant="caption" sx={{ color: '#6b7280', fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', mb: 0.5, display: 'block', fontSize: '10px' }}>
                            Credits Used
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 0.75 }}>
                            <Typography variant="h4" sx={{ fontWeight: 600, color: '#111827', letterSpacing: '-0.02em', fontSize: '28px' }}>
                                {totalUsed.toLocaleString()}
                            </Typography>
                            <Typography variant="body2" sx={{ color: '#9ca3af', fontWeight: 500 }}>
                                / {totalMax.toLocaleString()} credits
                            </Typography>
                        </Box>
                    </Box>
                    <Chip
                        label={plan.toUpperCase()}
                        size="medium"
                        sx={{
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            fontSize: '10px',
                            bgcolor: badgeColors.bg,
                            color: badgeColors.color,
                            borderRadius: '8px',
                            border: `1px solid ${badgeColors.border}`,
                            px: 1.5,
                            height: '28px',
                        }}
                    />
                </Box>

                <Box sx={{ position: 'relative', mb: 2.5 }}>
                    <LinearProgress
                        variant="determinate"
                        value={Math.min(usagePercent, 100)}
                        sx={{
                            height: 12,
                            borderRadius: 6,
                            bgcolor: '#f3f4f6',
                            '& .MuiLinearProgress-bar': {
                                borderRadius: 6,
                                background: getProgressColor(),
                                transition: 'all 0.5s ease',
                            }
                        }}
                    />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ color: isOverage ? '#ef4444' : '#6b7280', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '13px' }}>
                        {isOverage ? (
                            <>⚠️ Capacity reached</>
                        ) : (
                            <>{remainingUnits.toLocaleString()} credits left</>
                        )}
                    </Typography>

                    <Button
                        size="small"
                        onClick={() => router.push('/pricing')}
                        sx={{
                            textTransform: 'none',
                            color: 'rgba(3, 105, 161, 1)',
                            fontWeight: 600,
                            fontSize: '12px',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: '6px',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                                bgcolor: 'rgba(3, 105, 161, 0.05)',
                            }
                        }}
                    >
                        Get More Credits
                    </Button>
                </Box>

                {isOverage && (
                    <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(239, 68, 68, 0.05)', borderRadius: '10px', border: '1px dashed rgba(239, 68, 68, 0.25)' }}>
                        <Typography variant="caption" sx={{ color: '#ef4444', fontWeight: 500, display: 'block', fontSize: '12px' }}>
                            Extra usage costs ${engineCredits?.overageRate || 0.19} per credit.
                        </Typography>
                    </Box>
                )}
            </Box>
        </Paper>
        */
        null
    );
};

export default UsageDisplay;

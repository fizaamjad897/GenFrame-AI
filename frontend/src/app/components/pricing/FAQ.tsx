'use client';

import { Box, Typography, Container, Accordion, AccordionSummary, AccordionDetails, Button } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';

export default function FAQSection() {
    const faqs = [
        {
            q: "How do image credits work?",
            a: "Credits are used to process images. Each image generated or resized consumes exactly 1 credit. Your credit count depends on your selected plan and resets at the start of every billing cycle."
        },
        {
            q: "What image formats are supported?",
            a: "Recreative AI supports all major formats including PNG, JPG, WEBP, and TIFF. Our AI can output high-resolution files optimized for both digital and print media."
        },
        {
            q: "What happens if I exceed my monthly limit?",
            a: "Every plan includes Overage Flexibility. If you go beyond your included volume, additional credits are automatically applied at a flat rate of $0.19 per credit, ensuring your workflow is never interrupted."
        },
        {
            q: "Is the output ADA compliant?",
            a: "Yes! Our platform features a built-in accessibility layer that automatically optimizes font sizes, color contrast, and spacing to meet WCAG 2.1 standards."
        },
        {
            q: "Can I cancel or change my plan anytime?",
            a: "Absolutely. You can upgrade, downgrade, or cancel your subscription at any time directly from your account settings. Changes take effect at the start of the next billing period."
        }
    ];

    return (
        <Box sx={{
            py: { xs: 12, md: 15 },
            bgcolor: '#ffffff'
        }}>
            <Container maxWidth="md">
                <Box textAlign="center" mb={10}>
                    <Box sx={{
                        display: 'inline-flex',
                        p: 2,
                        bgcolor: 'rgba(139, 92, 246, 0.05)',
                        borderRadius: '20px',
                        mb: 3,
                        border: '1px solid rgba(139, 92, 246, 0.1)'
                    }}>
                        <QuestionAnswerIcon sx={{ color: 'rgba(139, 92, 246, 1)', fontSize: 28 }} />
                    </Box>
                    <Typography
                        variant="h2"
                        sx={{
                            fontWeight: 600,
                            color: '#111827',
                            mb: 2,
                            fontSize: { xs: '32px', md: '42px' },
                            letterSpacing: '-0.03em'
                        }}
                    >
                        Common Inquiries
                    </Typography>
                    <Typography
                        sx={{
                            color: '#6B7280',
                            fontSize: '18px',
                            fontWeight: 400,
                            maxWidth: '500px',
                            mx: 'auto'
                        }}
                    >
                        Everything you need to know about scaling your visual infrastructure.
                    </Typography>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {faqs.map((faq, i) => (
                        <Accordion
                            key={i}
                            elevation={0}
                            sx={{
                                borderRadius: '16px !important',
                                border: '1px solid rgba(139, 92, 246, 0.15)',
                                bgcolor: 'rgba(255, 255, 255, 0.8)',
                                backdropFilter: 'blur(20px)',
                                '&:before': { display: 'none' },
                                overflow: 'hidden',
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    borderColor: 'rgba(139, 92, 246, 0.4)',
                                    boxShadow: '0 10px 20px -5px rgba(139, 92, 246, 0.1)'
                                },
                                '& .MuiAccordionSummary-root': {
                                    py: 1,
                                    '&.Mui-expanded': {
                                        bgcolor: 'rgba(139, 92, 246, 0.05)',

                                    }
                                }
                            }}
                        >
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon sx={{ color: 'rgba(139, 92, 246, 1)' }} />}
                                sx={{ px: { xs: 3, md: 4 } }}
                            >
                                <Typography sx={{ fontWeight: 500, color: '#111827', fontSize: '17px' }}>
                                    {faq.q}
                                </Typography>
                            </AccordionSummary>
                            <AccordionDetails sx={{ px: { xs: 3, md: 4 }, pb: 4, pt: 1 }}>
                                <Typography sx={{ color: '#4b5563', lineHeight: 1.8, fontSize: '15px', fontWeight: 400 }}>
                                    {faq.a}
                                </Typography>
                            </AccordionDetails>
                        </Accordion>
                    ))}
                </Box>

                <Box textAlign="center" mt={12}>
                    <Box
                        sx={{
                            p: 5,
                            borderRadius: '24px',
                            border: '1px solid rgba(139, 92, 246, 0.2)',
                            bgcolor: 'rgba(255, 255, 255, 0.6)',
                            backdropFilter: 'blur(40px)'
                        }}
                    >
                        <Typography sx={{ color: '#111827', fontWeight: 500, mb: 1.5, fontSize: '18px' }}>
                            Still have questions?
                        </Typography>
                        <Typography sx={{ color: '#6B7280', mb: 4, fontSize: '15px', fontWeight: 400 }}>
                            Our support team is here to help you get started.
                        </Typography>
                        <Button
                            variant="contained"
                            component="a"
                            href="mailto:slidexyofficial@gmail.com"
                            sx={{
                                borderRadius: '18px',
                                textTransform: 'none',
                                fontWeight: 500,
                                px: 5,
                                py: 1.5,
                                bgcolor: 'rgba(139, 92, 246, 1)',
                                color: 'white',
                                boxShadow: '0 10px 20px -5px rgba(139, 92, 246, 0.3)',
                                '&:hover': {
                                    bgcolor: 'rgba(85, 55, 150, 1)',

                                    transform: 'translateY(-1px)',
                                    boxShadow: '0 15px 30px -8px rgba(139, 92, 246, 0.4)'
                                }
                            }}
                        >
                            Contact Support
                        </Button>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
}

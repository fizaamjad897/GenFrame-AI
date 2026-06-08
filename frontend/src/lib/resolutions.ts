export interface ResolutionPreset {
    id: string;
    label: string;
    ratio: string;
    category: string;
}

export const RESOLUTION_PRESETS: ResolutionPreset[] = [
    // Standard Options
    { id: 'landscape', label: 'Landscape', ratio: '16:9', category: 'Standard' },
    { id: 'story', label: 'Story/Reel', ratio: '9:16', category: 'Standard' },
    { id: 'square', label: 'Square', ratio: '1:1', category: 'Standard' },
    { id: 'portrait', label: 'Portrait', ratio: '3:4', category: 'Standard' },
    { id: 'ultrawide', label: 'Ultrawide', ratio: '21:9', category: 'Standard' },

    // Priority Custom Resolutions
    { id: 'custom-288-608', label: '288x608', ratio: '288:608', category: 'Custom' },
    { id: 'custom-324-828', label: '324x828', ratio: '324:828', category: 'Custom' },
    { id: 'custom-432-864', label: '432x864', ratio: '432:864', category: 'Custom' },
    { id: 'custom-396-576', label: '396x576', ratio: '396:576', category: 'Custom' },
    { id: 'custom-576-396', label: '576x396', ratio: '576:396', category: 'Custom' },
    { id: 'custom-624-336', label: '624x336', ratio: '624:336', category: 'Custom' },
];

export const PRESET_CATEGORIES = Array.from(new Set(RESOLUTION_PRESETS.map(p => p.category)));

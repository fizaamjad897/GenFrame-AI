export interface Engine {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
}

export const enginesData: Engine[] = [
  {
    id: "transformation",
    name: "Transformation Engine",
    description: "Convert and transform visual content into various formats",
    capabilities: [
      "Real-time image transformation",
      "Multiple resolution support",
      "Format conversion",
      "Aspect ratio adjustments",
    ],
  },
  {
    id: "creation",
    name: "Creation Engine",
    description: "Generate and create visual content from templates and specifications",
    capabilities: [
      "Template-based content generation",
      "Dynamic content creation",
      "AI-assisted design suggestions",
      "Customizable output formats",
    ],
  },
];

export interface EngineSelection {
  engines: string[]; // array of 'transformation', 'creation', or both
  transformationCreditsThreshold: number;
  transformationCreditPrice: number;
  creationCreditsThreshold: number;
  creationCreditPrice: number;
}

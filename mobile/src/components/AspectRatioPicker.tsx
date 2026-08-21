import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { ASPECT_RATIO_PRESETS } from '../types/models';

interface Props {
  value: string;
  onChange: (ratio: string) => void;
}

export default function AspectRatioPicker({ value, onChange }: Props) {
  return (
    <View style={styles.row}>
      {ASPECT_RATIO_PRESETS.map((preset) => {
        const selected = preset.ratio === value;
        return (
          <TouchableOpacity
            key={preset.key}
            style={[styles.chip, selected && styles.chipSelected]}
            onPress={() => onChange(preset.ratio)}
          >
            <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
              {preset.label}
            </Text>
            <Text style={[styles.chipSubtext, selected && styles.chipTextSelected]}>
              {preset.ratio}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: 'rgba(3, 105, 161, 0.2)',
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  chipSelected: {
    backgroundColor: 'rgba(3, 105, 161, 1)',
    borderColor: 'rgba(3, 105, 161, 1)',
  },
  chipText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#111827',
  },
  chipSubtext: {
    fontSize: 11,
    color: '#6b7280',
    marginTop: 2,
  },
  chipTextSelected: {
    color: '#fff',
  },
});

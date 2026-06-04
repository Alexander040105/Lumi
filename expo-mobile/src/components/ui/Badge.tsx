import { StyleSheet, Text, View } from 'react-native';
import { useTheme } from '@/hooks/useTheme';

interface BadgeProps {
  title: string;
  variant?: 'default' | 'secondary' | 'destructive' | 'warning';
}

export default function Badge({ title, variant = 'default' }: BadgeProps) {
  const { colors } = useTheme();

  const backgroundColor =
    variant === 'destructive'
      ? colors.destructive
      : variant === 'warning'
        ? colors.warning
        : variant === 'secondary'
          ? colors.secondary
          : colors.primary;

  const color =
    variant === 'destructive'
      ? colors.destructiveForeground
      : variant === 'warning'
        ? '#ffffff'
        : variant === 'secondary'
          ? colors.secondaryForeground
          : colors.primaryForeground;

  return (
    <View style={[styles.badge, { backgroundColor }]}>
      <Text style={[styles.text, { color }]}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 999,
    alignSelf: 'flex-start',
  },
  text: {
    fontSize: 10,
    fontWeight: '500',
  },
});

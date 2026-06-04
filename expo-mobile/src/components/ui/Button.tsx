import {
  StyleSheet,
  Text,
  TouchableOpacity,
  TouchableOpacityProps,
} from 'react-native';
import { useTheme } from '@/hooks/useTheme';

interface ButtonProps extends TouchableOpacityProps {
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm';
  title: string;
}

export default function Button({
  variant = 'default',
  size = 'default',
  title,
  style,
  disabled,
  ...props
}: ButtonProps) {
  const { colors } = useTheme();

  const backgroundColor =
    variant === 'default'
      ? colors.primary
      : variant === 'outline' || variant === 'ghost'
        ? 'transparent'
        : colors.primary;

  const borderColor =
    variant === 'outline' ? colors.border : 'transparent';

  const color =
    variant === 'default'
      ? colors.primaryForeground
      : colors.foreground;

  const paddingVertical = size === 'sm' ? 6 : 10;
  const paddingHorizontal = size === 'sm' ? 12 : 16;
  const fontSize = size === 'sm' ? 12 : 14;

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      disabled={disabled}
      style={[
        styles.base,
        {
          backgroundColor: disabled ? colors.muted : backgroundColor,
          borderColor,
          borderWidth: variant === 'outline' ? 1 : 0,
          paddingVertical,
          paddingHorizontal,
          opacity: disabled ? 0.5 : 1,
        },
        style,
      ]}
      {...props}
    >
      <Text style={[styles.text, { color, fontSize }]}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontWeight: '500',
  },
});

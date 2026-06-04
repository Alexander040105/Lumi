import { StyleSheet, TextInput, TextInputProps } from 'react-native';
import { useTheme } from '@/hooks/useTheme';

interface InputProps extends TextInputProps {
  error?: string;
}

export default function Input({ style, error, ...props }: InputProps) {
  const { colors } = useTheme();
  return (
    <TextInput
      placeholderTextColor={colors.mutedForeground}
      style={[
        styles.input,
        {
          backgroundColor: colors.background,
          borderColor: error ? colors.destructive : colors.input,
          color: colors.foreground,
        },
        style,
      ]}
      {...props}
    />
  );
}

const styles = StyleSheet.create({
  input: {
    height: 40,
    borderRadius: 6,
    borderWidth: 1,
    paddingHorizontal: 12,
    fontSize: 14,
  },
});

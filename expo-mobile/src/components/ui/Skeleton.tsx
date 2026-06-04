import { StyleProp, StyleSheet, View, ViewProps, ViewStyle } from 'react-native';
import { useTheme } from '@/hooks/useTheme';

interface SkeletonProps extends ViewProps {
  width?: number | `${number}%` | 'auto';
  height?: number;
}

export default function Skeleton({
  width = '100%',
  height = 16,
  style,
  ...props
}: SkeletonProps) {
  const { colors } = useTheme();
  const skeletonStyle: StyleProp<ViewStyle> = [
    styles.skeleton,
    {
      width: width as ViewStyle['width'],
      height,
      backgroundColor: colors.muted,
    },
    style,
  ];
  return <View style={skeletonStyle} {...props} />;
}

const styles = StyleSheet.create({
  skeleton: {
    borderRadius: 4,
  },
});

import { StyleSheet, View } from 'react-native';
import Skeleton from '@/components/ui/Skeleton';

export default function LoadingSkeleton() {
  return (
    <View style={styles.container}>
      <Skeleton width="66%" height={24} />
      <Skeleton height={96} />
      <View style={styles.row}>
        <Skeleton height={64} style={{ flex: 1 }} />
        <Skeleton height={64} style={{ flex: 1 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: 12,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
});

import React from 'react';
import { View, Button, StyleSheet } from 'react-native';

type MissionNavProps = {
  onPrevious: () => void;
  onNext: () => void;
  isPreviousDisabled: boolean;
  isNextDisabled: boolean;
};

const MissionNav: React.FC<MissionNavProps> = ({
  onPrevious,
  onNext,
  isPreviousDisabled,
  isNextDisabled,
}) => {
  return (
    <View style={styles.navigationButtons}>
      <Button title="Previous" onPress={onPrevious} disabled={isPreviousDisabled} />
      <Button title="Next" onPress={onNext} disabled={isNextDisabled} />
    </View>
  );
};

const styles = StyleSheet.create({
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 20,
  },
});

export default MissionNav; 
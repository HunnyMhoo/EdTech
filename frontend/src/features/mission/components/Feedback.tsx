import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Toast, { BaseToast, ErrorToast } from 'react-native-toast-message';

const styles = StyleSheet.create({
  // Add any custom styles here if needed
  successToast: {
    borderLeftColor: 'green',
  },
  errorToast: {
    borderLeftColor: 'red',
  },
  contentContainer: {
    paddingHorizontal: 15,
  },
  title: {
    fontWeight: 'bold',
  },
  message: {
    fontSize: 14,
    color: '#333',
  },
});


/*
  1. Create the config
*/
export const toastConfig = {
  /*
    Overwrite 'success' type,
    by modifying the existing `BaseToast` component
  */
  success: (props: any) => (
    <BaseToast
      {...props}
      style={styles.successToast}
      contentContainerStyle={styles.contentContainer}
      text1Style={styles.title}
      text2Style={styles.message}
    />
  ),
  /*
    Overwrite 'error' type,
    by modifying the existing `ErrorToast` component
  */
  error: (props: any) => (
    <ErrorToast
      {...props}
      style={styles.errorToast}
      contentContainerStyle={styles.contentContainer}
      text1Style={styles.title}
      text2Style={styles.message}
    />
  ),
  /*
    Or create a completely new type - `tomatoToast`,
    building the layout from scratch.

    I've commented this out as we don't need it for now.
  */
  // tomatoToast: ({ text1, props }) => (
  //   <View style={{ height: 60, width: '100%', backgroundColor: 'tomato' }}>
  //     <Text>{text1}</Text>
  //     <Text>{props.uuid}</Text>
  //   </View>
  // )
}; 
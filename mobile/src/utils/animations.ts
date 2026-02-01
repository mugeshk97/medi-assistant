import { Animated, Easing } from 'react-native';

/**
 * Reusable animation presets for consistent motion throughout the app
 */

// Fade in animation
export const fadeIn = (
    animatedValue: Animated.Value,
    duration: number = 250,
    delay: number = 0
): Animated.CompositeAnimation => {
    return Animated.timing(animatedValue, {
        toValue: 1,
        duration,
        delay,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
    });
};

// Fade out animation
export const fadeOut = (
    animatedValue: Animated.Value,
    duration: number = 200
): Animated.CompositeAnimation => {
    return Animated.timing(animatedValue, {
        toValue: 0,
        duration,
        easing: Easing.in(Easing.ease),
        useNativeDriver: true,
    });
};

// Slide up animation
export const slideUp = (
    animatedValue: Animated.Value,
    duration: number = 300,
    delay: number = 0
): Animated.CompositeAnimation => {
    return Animated.timing(animatedValue, {
        toValue: 0,
        duration,
        delay,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
    });
};

// Scale animation with spring
export const scaleSpring = (
    animatedValue: Animated.Value,
    toValue: number = 1,
    friction: number = 7
): Animated.CompositeAnimation => {
    return Animated.spring(animatedValue, {
        toValue,
        friction,
        tension: 40,
        useNativeDriver: true,
    });
};

// Pulse animation (for empty states, loading, etc.)
export const pulse = (
    animatedValue: Animated.Value,
    minValue: number = 0.95,
    maxValue: number = 1.05,
    duration: number = 1000
): Animated.CompositeAnimation => {
    return Animated.loop(
        Animated.sequence([
            Animated.timing(animatedValue, {
                toValue: maxValue,
                duration: duration / 2,
                easing: Easing.inOut(Easing.ease),
                useNativeDriver: true,
            }),
            Animated.timing(animatedValue, {
                toValue: minValue,
                duration: duration / 2,
                easing: Easing.inOut(Easing.ease),
                useNativeDriver: true,
            }),
        ])
    );
};

// Float animation (gentle up and down motion)
export const float = (
    animatedValue: Animated.Value,
    distance: number = 10,
    duration: number = 2000
): Animated.CompositeAnimation => {
    return Animated.loop(
        Animated.sequence([
            Animated.timing(animatedValue, {
                toValue: -distance,
                duration: duration / 2,
                easing: Easing.inOut(Easing.sin),
                useNativeDriver: true,
            }),
            Animated.timing(animatedValue, {
                toValue: 0,
                duration: duration / 2,
                easing: Easing.inOut(Easing.sin),
                useNativeDriver: true,
            }),
        ])
    );
};

// Stagger animation for lists
export const staggerList = (
    items: Animated.Value[],
    animationFn: (value: Animated.Value, delay: number) => Animated.CompositeAnimation,
    staggerDelay: number = 50
): Animated.CompositeAnimation => {
    const animations = items.map((item, index) =>
        animationFn(item, index * staggerDelay)
    );
    return Animated.parallel(animations);
};

// Button press animation
export const buttonPress = (
    animatedValue: Animated.Value,
    onPressIn: () => void,
    onPressOut: () => void
) => {
    return {
        onPressIn: () => {
            Animated.spring(animatedValue, {
                toValue: 0.95,
                useNativeDriver: true,
            }).start();
            onPressIn();
        },
        onPressOut: () => {
            Animated.spring(animatedValue, {
                toValue: 1,
                friction: 5,
                tension: 40,
                useNativeDriver: true,
            }).start();
            onPressOut();
        },
    };
};

// Rotate animation
export const rotate = (
    animatedValue: Animated.Value,
    toValue: number = 1,
    duration: number = 300
): Animated.CompositeAnimation => {
    return Animated.timing(animatedValue, {
        toValue,
        duration,
        easing: Easing.linear,
        useNativeDriver: true,
    });
};

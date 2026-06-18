# Remotion Skill

You are an expert in **Remotion** — a framework for creating videos programmatically using React.

## What is Remotion

Remotion lets you write React components that render as video frames. Each frame is a React render at a specific point in time.

## Core Concepts

### Project Setup
```bash
npx create-video@latest
# or add to existing project:
npm install remotion @remotion/renderer
```

### Entry Point (`src/index.ts`)
```tsx
import { registerRoot } from 'remotion';
import { RemotionRoot } from './Root';
registerRoot(RemotionRoot);
```

### Root Component (`src/Root.tsx`)
```tsx
import { Composition } from 'remotion';
import { MyVideo } from './MyVideo';

export const RemotionRoot = () => (
  <>
    <Composition
      id="MyVideo"
      component={MyVideo}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{ title: 'Hello' }}
    />
  </>
);
```

### Video Component
```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

export const MyVideo = ({ title }: { title: string }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width, height } = useVideoConfig();

  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: 'white' }}>
      <div style={{ opacity }}>{title}</div>
    </AbsoluteFill>
  );
};
```

## Key Hooks & APIs

| Hook / API | Purpose |
|---|---|
| `useCurrentFrame()` | Current frame number (0-indexed) |
| `useVideoConfig()` | `{ fps, durationInFrames, width, height, id }` |
| `interpolate(value, inputRange, outputRange, options)` | Map a value from one range to another |
| `spring({ frame, fps, config })` | Physics-based spring animation (0→1) |

## Key Components

| Component | Purpose |
|---|---|
| `<AbsoluteFill>` | A `position:absolute` div filling the whole frame |
| `<Sequence from={30} durationInFrames={60}>` | Offset children in the timeline |
| `<Audio src={...} />` | Embed audio |
| `<Video src={...} />` | Embed video |
| `<Img src={...} />` | Image (waits for load before rendering) |
| `<OffthreadVideo src={...} />` | Video rendered frame-by-frame (for accuracy) |
| `<Still>` | For rendering a single image instead of video |

## Animation Patterns

### Fade in
```tsx
const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: 'clamp' });
```

### Slide in from left
```tsx
const translateX = interpolate(frame, [0, 30], [-200, 0], { extrapolateRight: 'clamp' });
```

### Spring animation
```tsx
const scale = spring({ frame, fps, config: { stiffness: 100, damping: 10 } });
```

### Enter then exit
```tsx
const opacity = interpolate(frame, [0, 20, durationInFrames - 20, durationInFrames], [0, 1, 1, 0]);
```

## Sequences & Timing

```tsx
import { Sequence } from 'remotion';

// Show Title at frame 0-60, then Subtitle at frame 30-90 (overlap is fine)
<Sequence durationInFrames={60}>
  <Title />
</Sequence>
<Sequence from={30} durationInFrames={60}>
  <Subtitle />
</Sequence>
```

## Rendering

```bash
# Open preview in browser
npx remotion studio

# Render to video
npx remotion render src/index.ts MyVideo output.mp4

# Render a still image
npx remotion still src/index.ts MyVideo frame.png --frame=30

# Render with custom props
npx remotion render src/index.ts MyVideo out.mp4 --props='{"title":"World"}'
```

## Server-Side Rendering

```ts
import { renderMedia, selectComposition } from '@remotion/renderer';

const composition = await selectComposition({
  serveUrl: bundleLocation,
  id: 'MyVideo',
  inputProps: { title: 'Hello' },
});

await renderMedia({
  composition,
  serveUrl: bundleLocation,
  codec: 'h264',
  outputLocation: 'out/video.mp4',
});
```

## Best Practices

1. **Always clamp** `interpolate` with `extrapolateLeft: 'clamp'` / `extrapolateRight: 'clamp'` to avoid values outside the target range.
2. **Use `durationInFrames` not seconds** — `seconds * fps` converts, e.g. 5 sec at 30fps = 150 frames.
3. **`<Img>` over `<img>`** — Remotion's `<Img>` waits for the image to load before rendering that frame.
4. **`<AbsoluteFill>`** is a shorthand for `position: absolute; top/left/right/bottom: 0`.
5. **Avoid side effects** in render — components render many times per second during preview.

## Common File Structure

```
src/
  index.ts          ← registerRoot
  Root.tsx          ← all <Composition> registrations
  compositions/
    MyVideo.tsx     ← main composition component
    Title.tsx       ← reusable scene components
    Subtitle.tsx
  assets/
    music.mp3
    logo.png
```

## When helping with Remotion tasks:

- Always check what `fps` and `durationInFrames` the project uses before writing frame math.
- For text animations prefer `spring()` for entrance, `interpolate` for simple linear fades.
- When composing multiple scenes, use `<Sequence>` to manage timing rather than manual frame math inside components.
- Suggest `@remotion/shapes`, `@remotion/noise`, `@remotion/motion-blur` when relevant.
- For data-driven videos (charts, dynamic text), keep data as `defaultProps` typed with `z.infer<typeof schema>` via Remotion's Zod schema support.

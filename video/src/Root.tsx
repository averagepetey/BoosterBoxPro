import "./index.css";
import { Composition } from "remotion";
import { ExtensionDemo } from "./ExtensionDemo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ExtensionDemo"
      component={ExtensionDemo}
      durationInFrames={360}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};

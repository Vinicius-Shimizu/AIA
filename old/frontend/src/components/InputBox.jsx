"use client";
import { forwardRef, useImperativeHandle, useRef, useState, useLayoutEffect } from "react";
const MIN_HEIGHT = 80;
const MAX_HEIGHT = 160;

const InputBox = forwardRef(({ onEnter }, ref) => {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);
  const [height, setHeight] = useState(MIN_HEIGHT + "px");
  
  useImperativeHandle(ref, () => ({
    getValue: () => value,
    clear: () => {
      setValue("");
      setHeight(MIN_HEIGHT + "px");
    },
  }));

  useLayoutEffect(() => {
    const currentTextAreaRef = textareaRef.current;
    if (!currentTextAreaRef) return;

    const currentHeight = currentTextAreaRef.offsetHeight;

    currentTextAreaRef.style.height = "auto";
    const naturalHeight = currentTextAreaRef.scrollHeight;

    const nextHeight = Math.min(
      Math.max(naturalHeight, MIN_HEIGHT),
      MAX_HEIGHT
    );

    if (nextHeight !== currentHeight) {
      setHeight(nextHeight + "px");
    }

    currentTextAreaRef.style.height = height;
  }, [value, height]);

  const handleKeyDown = (e) => {
    if(e.key === "Enter" && !e.shiftKey){
      e.preventDefault();
      onEnter?.();
    }
  }

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onKeyDown={handleKeyDown}
      style={{ height }}
      className="border border-stone-300 w-[700px] rounded-md p-2 m-4 resize-none overflow-auto transition-[height] duration-150 ease-out"
      placeholder="Type your message..."
    />
  );
});

export default InputBox;
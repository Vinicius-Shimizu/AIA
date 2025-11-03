"use client";
import { forwardRef, useImperativeHandle, useRef } from "react";

const InputBox = forwardRef((props, ref) => {
  const textAreaRef = useRef();
  
  useImperativeHandle(ref, () =>({
    getValue: () => textAreaRef.current.value,
    clear: () => (textAreaRef.current.value = "")
  }));

  return (
    <textarea
      ref={textAreaRef}
      className="border border-stone-300 w-[700px] max-h-[80px] rounded-md p-2 m-4 resize-none overflow-auto"
      placeholder="Type your message..."
    />
  );
});

export default InputBox;
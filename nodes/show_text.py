import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const textAreaStyles = {
    readOnly: true,
    padding: '2px',
    paddingLeft: '7px',
    border: '1px solid #999',
    borderRadius: '4px',
    backgroundColor: '#333',
    color: 'silver',
    fontFamily: 'Arial, sans-serif',
    fontSize: '12px',
    lineHeight: '1.2',
    resize: 'vertical',
    overflowY: 'auto',
    width: '98%',
    minHeight: '50px',
    boxSizing: 'border-box',
};

app.registerExtension({
    name: "YourExtension.ShowText64Widget",

    async beforeRegisterNodeDef(nodeType, nodeData, appInstance) {
        if (nodeData.name === "ShowText64") {

            const textWidgetName = "No text to display";
            const buttonWidgetName = "Copy Text";

            function populate(textValue) {
                if (typeof textValue !== 'string') {
                    console.warn("ShowText64 populate: expects a string, got:", typeof textValue, textValue);
                    textValue = String(textValue !== undefined && textValue !== null ? textValue : "");
                }

                if (!this.widgets) {
                    this.widgets = [];
                }

                const existingTextWidgetIndex = this.widgets.findIndex((w) => w.name === textWidgetName);
                if (existingTextWidgetIndex !== -1) {
                    this.widgets[existingTextWidgetIndex].onRemove?.();
                    this.widgets.splice(existingTextWidgetIndex, 1);
                }

                const existingButtonWidgetIndex = this.widgets.findIndex((w) => w.name === buttonWidgetName);
                if (existingButtonWidgetIndex !== -1) {
                    this.widgets[existingButtonWidgetIndex].onRemove?.();
                    this.widgets.splice(existingButtonWidgetIndex, 1);
                }

                const textWidget = ComfyWidgets["STRING"](this, textWidgetName, ["STRING", { multiline: true }], appInstance).widget;
                textWidget.inputEl.readOnly = true;
                Object.assign(textWidget.inputEl.style, textAreaStyles);
                textWidget.value = textValue;

                const copyButton = this.addWidget(
                    "button",               
                    buttonWidgetName,       
                    "Copy Text",            
                    () => {                 
                        if (textWidget && textWidget.value) { 
                            navigator.clipboard.writeText(textWidget.value)
                                .then(() => {
                                    const originalLabel = copyButton.name; 
                                    copyButton.name = "Copied!";    
                                    this.setDirtyCanvas(true, false); 
                                    setTimeout(() => {
                                        copyButton.name = originalLabel; 
                                        this.setDirtyCanvas(true, false);
                                    }, 1000);
                                })
                                .catch(err => {
                                    console.error("ShowText64: Failed to copy text:", err);
                                    const originalLabel = copyButton.name;
                                    copyButton.name = "Error Copying!";
                                    this.setDirtyCanvas(true, false);
                                    setTimeout(() => {
                                        copyButton.name = originalLabel;
                                        this.setDirtyCanvas(true, false);
                                    }, 1500);
                                });
                        } else {
                            console.warn("ShowText64: No text to copy or text widget not found.");
                        }
                    },
                    {} 
                );               

                requestAnimationFrame(() => {
                    const sz = this.computeSize(); 
                    if (this.onResize) {
                        this.onResize(sz);
                    }
                    appInstance.graph.setDirtyCanvas(true, true);
                });
            }

            const onExecutedOriginal = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecutedOriginal?.apply(this, arguments);
                if (message && message.text !== undefined) {
                    let textToShow = message.text;
                    if (Array.isArray(message.text)) {
                        textToShow = message.text.join("").trim();
                    } else if (typeof message.text === 'string') {
                        textToShow = message.text.trim();
                    } else {
                        textToShow = String(message.text);
                    }
                    populate.call(this, textToShow);
                } else {
                    populate.call(this, "");
                    console.warn("ShowText64: No 'text' property in UI message:", message);
                }
            };

            const onConfigureOriginal = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function (data) {
                onConfigureOriginal?.apply(this, arguments);
                if (this.widgets_values && this.widgets_values.length > 0 && this.widgets_values[0] !== undefined) {
                    populate.call(this, String(this.widgets_values[0]));
                } else {
                    const textInput = this.inputs?.find(i => i.name === "text");
                    populate.call(this, textInput?.value || "");
                }
            };

            const onNodeCreatedOriginal = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreatedOriginal?.apply(this, arguments);
                const textInput = this.inputs?.find(i => i.name === "text");
                populate.call(this, textInput?.value || ""); 
            };
        }
    }
});

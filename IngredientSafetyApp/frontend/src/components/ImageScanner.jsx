import React, { useState, useRef } from 'react';
import Tesseract from 'tesseract.js';
import { Camera, Upload, Loader2, X, Check } from 'lucide-react';

const ImageScanner = ({ onScanComplete, isLoading: parentLoading }) => {
    const [image, setImage] = useState(null);
    const [isScanning, setIsScanning] = useState(false);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setImage(e.target.result);
                processImage(file);
            };
            reader.readAsDataURL(file);
        }
    };

    const processImage = async (file) => {
        setIsScanning(true);
        setStatus('Initializing OCR engine...');
        setProgress(0);

        try {
            // Tesseract v6/v7: createWorker('eng', 1, { logger })
            // 1 = OEM.DEFAULT
            const worker = await Tesseract.createWorker('eng', 1, {
                logger: m => {
                    if (m.status === 'recognizing text') {
                        setProgress(Math.round(m.progress * 100));
                        setStatus(`Scanning... ${Math.round(m.progress * 100)}%`);
                    } else {
                        setStatus(m.status);
                    }
                }
            });

            setStatus('Extracting text...');
            const { data: { text } } = await worker.recognize(file);

            await worker.terminate();
            onScanComplete(text);
            setIsScanning(false);
            setStatus('Complete!');
        } catch (error) {
            console.error(error);
            setStatus(`Failed: ${error.message || 'Unknown error'}`);
            setIsScanning(false);
        }
    };

    const clearImage = () => {
        setImage(null);
        setProgress(0);
        setStatus('');
    };

    return (
        <div className="w-full">
            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/*"
                onChange={handleFileSelect}
            />

            {!image ? (
                <div className="grid grid-cols-2 gap-4">
                    <button
                        type="button"
                        onClick={() => fileInputRef.current.click()}
                        disabled={parentLoading || isScanning}
                        className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-white/20 rounded-xl hover:bg-white/5 hover:border-white/40 transition-all group"
                    >
                        <Upload className="mb-2 text-primary group-hover:scale-110 transition-transform" size={32} />
                        <span className="text-sm font-medium text-gray-300">Upload Photo</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => fileInputRef.current.click()} // In real mobile app, could use native camera API
                        disabled={parentLoading || isScanning}
                        className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-white/20 rounded-xl hover:bg-white/5 hover:border-white/40 transition-all group"
                    >
                        <Camera className="mb-2 text-emerald-400 group-hover:scale-110 transition-transform" size={32} />
                        <span className="text-sm font-medium text-gray-300">Take Photo</span>
                    </button>
                </div>
            ) : (
                <div className="relative rounded-xl overflow-hidden bg-black/40 border border-white/10">
                    <img src={image} alt="Scanned" className="w-full h-48 object-cover opacity-70" />

                    <button
                        onClick={clearImage}
                        className="absolute top-2 right-2 p-1 bg-black/50 rounded-full hover:bg-red-500/80 transition-colors"
                    >
                        <X size={16} className="text-white" />
                    </button>

                    <div className="absolute inset-0 flex flex-col items-center justify-center p-4">
                        {isScanning ? (
                            <div className="text-center w-full max-w-xs bg-black/60 p-4 rounded-xl backdrop-blur-sm">
                                <Loader2 className="animate-spin mx-auto text-primary mb-2" size={32} />
                                <p className="text-white font-medium mb-2">{status}</p>
                                <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                    <div
                                        className="bg-primary h-full transition-all duration-300"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                            </div>
                        ) : (
                            <div className="bg-emerald-500/90 text-white px-4 py-2 rounded-full flex items-center gap-2 shadow-lg backdrop-blur-sm">
                                <Check size={18} />
                                <span className="font-bold">Scan Complete!</span>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ImageScanner;

import React from 'react';
import { Product } from '../../api/realApi';
import { ExternalLink, ShoppingBag, Star } from 'lucide-react'; // Ensure lucide-react is installed

interface ProductCardProps {
    product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
    return (
        <div className="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300 w-full max-w-xs mx-2 my-2 group">
            <div className="relative h-48 overflow-hidden bg-gray-50 dark:bg-gray-900">
                <img
                    src={product.image}
                    alt={product.name}
                    className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                        (e.target as HTMLImageElement).src = 'https://placehold.co/300x300?text=Product+Image';
                    }}
                />
                <div className="absolute top-2 right-2 bg-white/90 dark:bg-black/80 backdrop-blur-sm px-2 py-1 rounded-full text-xs font-semibold text-gray-700 dark:text-gray-300 shadow-sm border border-gray-200 dark:border-gray-600">
                   {product.marketplace}
                </div>
            </div>

            <div className="p-4 flex flex-col flex-1">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 line-clamp-2 mb-2 text-sm h-10 leading-tight">
                    {product.name}
                </h3>
                
                <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-4 italic flex-1">
                   "{product.reason}"
                </p>

                <div className="mt-auto">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">
                            {product.price}
                        </span>
                        {/* Placeholder rating if you want */}
                         <div className="flex items-center text-amber-400">
                            <Star className="w-3 h-3 fill-current" />
                            <span className="text-xs text-gray-600 dark:text-gray-400 ml-1">4.5</span>
                         </div>
                    </div>

                    <a
                        href={product.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-full py-2.5 px-4 bg-gray-900 hover:bg-gray-800 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 gap-2 shadow-sm"
                    >
                        <ShoppingBag className="w-4 h-4" />
                        Buy Now
                        <ExternalLink className="w-3 h-3 opacity-70" />
                    </a>
                </div>
            </div>
        </div>
    );
}

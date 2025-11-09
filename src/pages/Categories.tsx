import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getCategories, deleteCategory, Category } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  ArrowLeft,
  Tag,
  Trash2,
  ShoppingCart,
  Home,
  Utensils,
  Car,
  DollarSign,
  Zap,
  Smartphone,
  Film,
  Tv,
  PiggyBank,
  Target,
  CreditCard,
  Landmark,
  Briefcase,
  Circle,
  Shield,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function Categories() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null);

  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      toast({
        title: 'Category Deleted',
        description: 'The category has been successfully deleted.',
      });
      setDeleteDialogOpen(false);
      setCategoryToDelete(null);
    },
    onError: (error: Error) => {
      toast({
        title: 'Error deleting category',
        description: error.message || 'Failed to delete category',
        variant: 'destructive',
      });
    },
  });

  const handleDelete = (category: Category) => {
    setCategoryToDelete(category);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (categoryToDelete) {
      deleteMutation.mutate(categoryToDelete.id);
    }
  };

  const iconMap: Record<string, React.ReactNode> = {
    ShoppingCart: <ShoppingCart className="h-5 w-5" />,
    Home: <Home className="h-5 w-5" />,
    Utensils: <Utensils className="h-5 w-5" />,
    Car: <Car className="h-5 w-5" />,
    DollarSign: <DollarSign className="h-5 w-5" />,
    Zap: <Zap className="h-5 w-5" />,
    Smartphone: <Smartphone className="h-5 w-5" />,
    Film: <Film className="h-5 w-5" />,
    Tv: <Tv className="h-5 w-5" />,
    PiggyBank: <PiggyBank className="h-5 w-5" />,
    Target: <Target className="h-5 w-5" />,
    CreditCard: <CreditCard className="h-5 w-5" />,
    Landmark: <Landmark className="h-5 w-5" />,
    Briefcase: <Briefcase className="h-5 w-5" />,
    Circle: <Circle className="h-5 w-5" />,
  };

  const getGroupColor = (group: string) => {
    switch (group) {
      case 'needs':
        return 'bg-blue-100 text-blue-800';
      case 'wants':
        return 'bg-purple-100 text-purple-800';
      case 'savings':
        return 'bg-green-100 text-green-800';
      case 'income':
        return 'bg-emerald-100 text-emerald-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Group categories by type
  const groupedCategories = categories.reduce((acc, category) => {
    const group = category.group || 'other';
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(category);
    return acc;
  }, {} as Record<string, Category[]>);

  const systemCategories = categories.filter((c) => c.is_system);
  const customCategories = categories.filter((c) => !c.is_system);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link to="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="p-2 rounded-lg bg-gradient-primary">
                <Tag className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Categories</h1>
                <p className="text-sm text-muted-foreground">Manage transaction categories</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Summary Card */}
          <Card>
            <CardHeader>
              <CardTitle>Category Summary</CardTitle>
              <CardDescription>
                {isLoading
                  ? 'Loading...'
                  : `${systemCategories.length} system categories, ${customCategories.length} custom categories`}
              </CardDescription>
            </CardHeader>
          </Card>

          {/* Categories List */}
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-64 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          ) : categories.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Tag className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-medium text-muted-foreground">No categories found</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupedCategories).map(([group, cats]) => (
                <Card key={group}>
                  <CardHeader>
                    <CardTitle className="capitalize">{group} Categories</CardTitle>
                    <CardDescription>{cats.length} categories in this group</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                      {cats.map((category) => (
                        <div
                          key={category.id}
                          className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary">
                              {iconMap[category.icon] || iconMap.Circle}
                            </div>
                            <div>
                              <div className="font-medium">{category.name}</div>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge className={getGroupColor(category.group)} variant="secondary">
                                  {category.group}
                                </Badge>
                                {category.is_system && (
                                  <Badge variant="outline" className="text-xs">
                                    <Shield className="h-3 w-3 mr-1" />
                                    System
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(category)}
                            disabled={category.is_system}
                            title={category.is_system ? 'System categories cannot be deleted' : 'Delete category'}
                          >
                            <Trash2
                              className={`h-4 w-4 ${
                                category.is_system ? 'text-muted-foreground' : 'text-destructive'
                              }`}
                            />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Category?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the category "{categoryToDelete?.name}"?
              <br />
              <br />
              <strong className="text-destructive">Warning:</strong> This may affect transactions
              using this category. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

